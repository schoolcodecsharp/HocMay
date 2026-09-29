from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_saved_pipeline_predicts_finite_value():
    pipeline = joblib.load(ROOT / "models" / "final_pipeline.joblib")
    schema = json.loads(
        (ROOT / "reports" / "results" / "input_schema.json").read_text(encoding="utf-8")
    )
    sample = pd.DataFrame(
        [{feature: bounds["median"] for feature, bounds in schema.items()}]
    )
    prediction = pipeline.predict(sample)
    assert prediction.shape == (1,)
    assert np.isfinite(prediction[0])


def test_results_are_not_placeholders():
    metrics = json.loads(
        (ROOT / "reports" / "results" / "metrics.json").read_text(encoding="utf-8")
    )
    assert metrics["selection"]["test_was_not_used_for_selection"] is True
    for split in ["validation", "test"]:
        for values in metrics[split].values():
            assert set(values) == {"mae", "rmse", "r2"}


def test_serving_pipeline_scaler_uses_train_only():
    from src.data import EXPECTED_FEATURES, load_california_housing
    from src.split import split_ids

    pipeline = joblib.load(ROOT / "models/final_pipeline.joblib")
    train = load_california_housing().iloc[split_ids()["train"]]
    scaler = pipeline.named_steps["scaler"]
    assert scaler.n_samples_seen_ == 14448
    np.testing.assert_allclose(scaler.mean_, train[EXPECTED_FEATURES].mean())


def test_serving_metrics_reuse_selected_candidate():
    from src.common import read_json, RESULTS, checksum

    metrics = read_json(RESULTS / "metrics.json")
    selected = metrics["selection"]["selected_model"]
    assert metrics["test"]["selected_pipeline"] == metrics["test"][selected]
    assert metrics["selection"]["serving_fit_scope"] == "train only"
    metadata = read_json(RESULTS / "model_metadata.json")
    assert metadata["model_sha256"] == checksum(ROOT / "models/final_pipeline.joblib")


def test_default_evaluation_never_loads_test(monkeypatch, tmp_path):
    import src.evaluate as evaluation

    def forbidden():
        raise AssertionError("Default evaluate must reuse frozen scores, not load test")

    monkeypatch.setattr(evaluation, "load_california_housing", forbidden)
    monkeypatch.setattr(evaluation, "save_json", lambda *args: None)
    evaluation.main()
