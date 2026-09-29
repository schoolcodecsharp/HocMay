from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_saved_pipeline_predicts_finite_value():
    pipeline = joblib.load(ROOT / "models" / "final_pipeline.joblib")
    schema = json.loads((ROOT / "reports" / "results" / "input_schema.json").read_text(encoding="utf-8"))
    sample = pd.DataFrame([{feature: bounds["median"] for feature, bounds in schema.items()}])
    prediction = pipeline.predict(sample)
    assert prediction.shape == (1,)
    assert np.isfinite(prediction[0])


def test_results_are_not_placeholders():
    metrics = json.loads((ROOT / "reports" / "results" / "metrics.json").read_text(encoding="utf-8"))
    assert metrics["selection"]["test_was_not_used_for_selection"] is True
    for split in ["validation", "test"]:
        for values in metrics[split].values():
            assert set(values) == {"mae", "rmse", "r2"}
