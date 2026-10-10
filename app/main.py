"""FastAPI phục vụ năm màn hình, CSDL chỉ đọc và API ước lượng."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
import sqlite3
from src.database import DB_PATH
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
app.mount(
    "/figures",
    StaticFiles(directory=ROOT / "reports" / "figures", check_dir=False),
    name="figures",
)
templates = Jinja2Templates(directory=APP_DIR / "templates")


@app.exception_handler(RequestValidationError)
async def invalid_request(request, error):
    details = [
        {"field": str(item["loc"][-1]), "message": item["msg"]}
        for item in error.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": details})


def read_json(name: str, fallback=None):
    path = RESULTS_DIR / name
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def common_context(request: Request, active: str) -> dict:
    return {"request": request, "active": active}


@app.get("/", response_class=HTMLResponse)
def introduction(request: Request):
    return templates.TemplateResponse(
        request, "index.html", common_context(request, "intro")
    )


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
        trials=read_json("sgd_trials.json", {}),
        groups=read_json("residual_groups.json", {}),
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
        raise HTTPException(
            status_code=503, detail="Model hoặc metadata chưa sẵn sàng."
        ) from error
    return {"status": "ok", "model": model_service.metadata["selected_model"]}


@app.post("/api/estimate", response_model=EstimateResponse)
def estimate(payload: EstimateRequest):
    try:
        model_service.ensure_loaded()
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="Model hoặc metadata chưa sẵn sàng. Kiểm tra artifact offline.",
        ) from error
    errors = model_service.validate_domain(payload.model_dump())
    if errors:
        raise HTTPException(status_code=422, detail=errors)
    try:
        prediction = model_service.predict(payload.model_dump())
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=500, detail="Không thể thực hiện prediction."
        ) from error

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


@app.get("/data", response_class=HTMLResponse)
def data_page(request: Request):
    context = common_context(request, "data")
    context["database"] = read_json("database_manifest.json", {})
    return templates.TemplateResponse(request, "data.html", context)


@app.get("/api/data")
def data_preview(
    offset: int = Query(0, ge=0, le=20640), limit: int = Query(20, ge=1, le=100)
):
    try:
        with sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True) as conn:
            conn.row_factory = sqlite3.Row
            total = conn.execute(
                "SELECT count(*) FROM housing_features WHERE split='train'"
            ).fetchone()[0]
            rows = conn.execute(
                "SELECT * FROM housing_features WHERE split='train' ORDER BY row_id LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return {
            "split": "train",
            "total": total,
            "offset": offset,
            "limit": limit,
            "rows": [dict(row) for row in rows],
        }
    except sqlite3.Error as error:
        raise HTTPException(
            503, detail="Chưa có CSDL. Chạy python -m src.database."
        ) from error
