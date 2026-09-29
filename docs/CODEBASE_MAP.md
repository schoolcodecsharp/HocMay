# Codebase Map

Cập nhật: 2026-09-29.

## Stack

Python, pandas, NumPy, scikit-learn, Matplotlib, FastAPI, Jinja2 và JavaScript thuần.

## Feature to file mapping

- Tải và xác minh dataset: `src/data.py`.
- Metric dùng chung: `src/metrics.py`.
- Split, train, SGD experiment, model selection, final test, artifact và figures: `src/train.py`.
- Đọc kết quả frozen: `src/evaluate.py`.
- FastAPI routes: `app/main.py`.
- Load/predict saved pipeline: `app/model_service.py`.
- API schema/domain validation: `app/schemas.py`.
- Templates: `app/templates/`.
- Design system và responsive layout: `app/static/css/styles.css`.
- Form/API interaction: `app/static/js/estimate.js`.
- Tests: `tests/test_api.py`, `tests/test_pipeline.py`.

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
- API không fit hoặc train.
- Dashboard đọc artifact thật, không hard-code metric.
- Prediction luôn kèm cảnh báo lịch sử/census block group.

## Verification commands

```powershell
.\.venv\Scripts\python.exe -m src.data
.\.venv\Scripts\python.exe -m src.train
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app.main:app
```

## Excluded directories

Không lập bản đồ `.venv/`, `.cache/`, `__pycache__/` và file CSV được tái tạo.
