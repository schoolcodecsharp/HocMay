"""FastAPI phục vụ ba màn hình và API ước lượng."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.model_service import ROOT, model_service
from app.schemas import EstimateRequest, EstimateResponse


APP_DIR = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "reports" / "results"

app = FastAPI(
    title="California Housing Lab API",
    version="1.0.0",
    description="Ước lượng MedHouseVal cho census block group từ dữ liệu lịch sử California.",
)
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
app.mount("/figures", StaticFiles(directory=ROOT / "reports" / "figures"), name="figures")
templates = Jinja2Templates(directory=APP_DIR / "templates")


def read_json(name: str, fallback=None):
    path = RESULTS_DIR / name
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def common_context(request: Request, active: str) -> dict:
    return {"request": request, "active": active}


@app.get("/", response_class=HTMLResponse)
def introduction(request: Request):
    return templates.TemplateResponse(request, "index.html", common_context(request, "intro"))


@app.get("/estimate", response_class=HTMLResponse)
def estimate_page(request: Request):
    context = common_context(request, "estimate")
    context["schema"] = read_json("input_schema.json", {})
    return templates.TemplateResponse(request, "estimate.html", context)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    context = common_context(request, "dashboard")
    context.update(
        metrics=read_json("metrics.json"),
        metadata=read_json("model_metadata.json"),
        quality=read_json("data_quality.json"),
        residual=read_json("residual_analysis.json"),
        coefficients=read_json("coefficients.json", []),
    )
    return templates.TemplateResponse(request, "dashboard.html", context)


@app.get("/model-card", response_class=HTMLResponse)
def model_card(request: Request):
    context = common_context(request, "model-card")
    context.update(
        metrics=read_json("metrics.json"),
        metadata=read_json("model_metadata.json"),
        quality=read_json("data_quality.json"),
    )
    return templates.TemplateResponse(request, "model_card.html", context)


@app.get("/api/health")
def health():
    try:
        model_service.ensure_loaded()
    except Exception as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"status": "ok", "model": model_service.metadata["selected_model"]}


@app.post("/api/estimate", response_model=EstimateResponse)
def estimate(payload: EstimateRequest):
    try:
        prediction = model_service.predict(payload.model_dump())
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail="Không thể thực hiện prediction.") from error

    return EstimateResponse(
        prediction=prediction,
        unit="100,000 USD",
        estimated_usd=prediction * 100_000,
        model=model_service.metadata["selected_model"],
        warning=(
            "Đây là ước lượng cho một census block group dựa trên dữ liệu lịch sử "
            "California khoảng năm 1990; không phải giá của một căn nhà cụ thể "
            "hoặc giá thị trường hiện tại."
        ),
    )
