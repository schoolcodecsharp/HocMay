# Codebase Map

Cập nhật: 2026-09-29.

## Stack

Python, pandas, NumPy, scikit-learn, Matplotlib, FastAPI, Jinja2 và JavaScript thuần.

## Feature to file mapping

- Tải và xác minh dataset: `src/data.py`.
- Metric dùng chung: `src/metrics.py`.
- Split cố định/ID: `src/split.py`; Pipeline: `src/features.py`.
- Train candidate, SGD, chọn bằng validation: `src/train.py`.
- Đọc kết quả frozen, hậu kiểm có chỉ định: `src/evaluate.py`.
- SQLite và đối chiếu cadata/sklearn: `src/database.py`, `data/schema.sql`.
- EDA train-only: `src/eda.py`; thí nghiệm/figures: `src/experiments.py`.
- Config/checksum/JSON: `src/common.py`.
- FastAPI routes: `app/main.py`.
- Load/predict saved pipeline: `app/model_service.py`.
- API schema/domain validation: `app/schemas.py`.
- Templates: `app/templates/`.
- Design system và responsive layout: `app/static/css/styles.css`.
- Form/API interaction: `app/static/js/estimate.js`.
- CSDL phân trang: `app/static/js/data.js`, `/data`, `/api/data`.
- Tests: `tests/test_api.py`, `tests/test_pipeline.py`, `tests/test_data.py`.
- Hướng dẫn chạy và tái lập: `README.md`, `docs/REPRODUCIBILITY.md`, `run.ps1`. Báo cáo/slide ngoài phạm vi theo yêu cầu mới.

## Shared artifacts

- Config: `config/project_config.json`.
- Dataset local, ignored by Git: `data/raw/`.
- Saved pipeline: `models/final_pipeline.joblib`.
- Machine-readable results: `reports/results/`.
- Dashboard charts: `reports/figures/`.

## Important invariants

- Split trước mọi preprocessing.
- Validation chọn model; test không tuning.
- Scaler luôn nằm trong Pipeline.
- Candidate và serving đều train-only. Artifact refit cũ giữ trong archive, migration có audit, không tuning lại hoặc coi hậu kiểm là test độc lập mới.
- API không fit hoặc train.
- Dashboard đọc artifact thật, không hard-code metric.
- Prediction luôn kèm cảnh báo lịch sử/census block group.

## Verification commands

```powershell
.\.venv\Scripts\python.exe -m src.data
.\.venv\Scripts\python.exe -m src.train
.\.venv\Scripts\python.exe -m src.database
.\.venv\Scripts\python.exe -m src.evaluate
.\.venv\Scripts\python.exe -m src.eda
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app.main:app
```

## Excluded directories

Không lập bản đồ `.venv/`, `.cache/`, `__pycache__/` và file CSV được tái tạo.

Receipt kiểm chứng: `reports/results/verification.json` (41 test đạt, clean venv và browser). `.build/` và `reports/qa/` là file tạm riêng, không commit.
