"""Xác minh artifact và đọc final test đã freeze; không test lại để tuning."""

import json
import argparse
import joblib
import numpy as np
from src.common import ROOT, RESULTS, read_json, save_json, checksum
from src.data import load_california_housing, EXPECTED_FEATURES, TARGET
from src.split import split_ids
from src.metrics import regression_metrics


def reproduce_once():
    """Kiểm chứng kết quả đã công bố; không phải thí nghiệm chọn model mới."""
    receipt = RESULTS / "reproduction_audit.json"
    frozen = read_json(RESULTS / "frozen_manifest.json")
    if (
        receipt.exists()
        and (RESULTS / "residual_rows.csv").exists()
        and read_json(receipt).get("model_sha256") == frozen["serving_model_sha256"]
    ):
        print("Reproduction already recorded. Using saved receipt.")
        return read_json(receipt)
    original = read_json(ROOT / "reports/archive/initial/metrics.json")
    if checksum(ROOT / "models/candidates.joblib") != frozen["candidate_sha256"]:
        raise RuntimeError("Candidate artifact changed.")
    test = load_california_housing().iloc[split_ids()["test"]]
    models = joblib.load(ROOT / "models/candidates.joblib")
    models["selected_pipeline"] = joblib.load(ROOT / "models/final_pipeline.joblib")
    metrics = {}
    for name, model in models.items():
        pred = model.predict(test[EXPECTED_FEATURES])
        metrics[name] = regression_metrics(test[TARGET], pred)
        expected_name = (
            frozen["selected_model"] if name == "selected_pipeline" else name
        )
        for metric, value in metrics[name].items():
            np.testing.assert_allclose(
                value, original["test"][expected_name][metric], rtol=1e-9, atol=1e-10
            )
        if name == "selected_pipeline":
            rows = test.copy()
            rows["predicted"] = pred
            rows["residual"] = test[TARGET] - pred
            rows.to_csv(RESULTS / "residual_rows.csv", index_label="row_id")
    result = {
        "kind": "post-hoc reproduction of already published test; not fresh independent evaluation",
        "matches_original": True,
        "model_sha256": frozen["serving_model_sha256"],
        "metrics": metrics,
    }
    save_json(receipt, result)
    return result


def main():
    frozen = read_json(RESULTS / "frozen_manifest.json")
    if (
        checksum(ROOT / "models/final_pipeline.joblib")
        != frozen["serving_model_sha256"]
    ):
        raise RuntimeError("Model differs from evaluated artifact.")
    if checksum(ROOT / "config/project_config.json") != frozen["config_sha256"]:
        raise RuntimeError("Config differs from frozen experiment.")
    # Test đã mở ở phiên bản đầu: giữ kết quả cũ, không giả là holdout mới.
    original = read_json(ROOT / "reports/archive/initial/metrics.json")
    original["test"]["selected_pipeline"] = original["test"][frozen["selected_model"]]
    save_json(RESULTS / "final_test_metrics.json", original["test"])
    print(
        json.dumps(
            {
                "status": "frozen candidate results reused; no new evaluation",
                "test": original["test"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reproduce",
        action="store_true",
        help="One-time audit against published metrics, never tuning",
    )
    args = parser.parse_args()
    main()
    if args.reproduce:
        reproduce_once()
