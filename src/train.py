"""Train offline và chọn model bằng validation. Không truy cập test."""

import json
import platform
from datetime import datetime, timezone
import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import SGDRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from src.common import ROOT, RESULTS, config, save_json, read_json, checksum
from src.data import EXPECTED_FEATURES, TARGET, load_california_housing
from src.features import linear_pipeline
from src.metrics import regression_metrics
from src.split import persist_split


def fit_candidates(train, validation, cfg):
    x, y = train[EXPECTED_FEATURES], train[TARGET]
    xv, yv = validation[EXPECTED_FEATURES], validation[TARGET]
    baseline = Pipeline([("model", DummyRegressor(strategy="mean"))]).fit(x, y)
    linear = linear_pipeline().fit(x, y)
    pipelines = {"mean_baseline": baseline, "linear_regression": linear}
    scores = {k: regression_metrics(yv, p.predict(xv)) for k, p in pipelines.items()}
    histories, trials, sgd_pipelines = {}, {}, {}
    for rate in cfg["sgd_learning_rates"]:
        scaler = StandardScaler().fit(x)
        xs, vs = scaler.transform(x), scaler.transform(xv)
        sgd = SGDRegressor(
            loss="squared_error",
            penalty=None,
            learning_rate="constant",
            eta0=rate,
            max_iter=1,
            tol=None,
            warm_start=True,
            shuffle=False,
            random_state=cfg["random_state"],
        )
        rng = np.random.default_rng(cfg["random_state"])
        history = []
        for epoch in range(1, cfg["sgd_epochs"] + 1):
            order = rng.permutation(len(x))
            sgd.partial_fit(xs[order], y.iloc[order])
            loss = float(np.mean((y.to_numpy() - sgd.predict(xs)) ** 2) / 2)
            val_loss = float(np.mean((yv.to_numpy() - sgd.predict(vs)) ** 2) / 2)
            if not np.isfinite([loss, val_loss]).all():
                raise ValueError(f"SGD non-finite loss at rate {rate}")
            history.append(
                {"epoch": epoch, "train_loss": loss, "validation_loss": val_loss}
            )
        key = str(rate)
        histories[key] = history
        trials[key] = regression_metrics(yv, sgd.predict(vs))
        sgd_pipelines[key] = Pipeline([("scaler", scaler), ("model", sgd)])
    best = min(trials, key=lambda k: trials[k]["rmse"])
    pipelines["sgd_regressor"] = sgd_pipelines[best]
    scores["sgd_regressor"] = trials[best]
    selected = min(
        ("linear_regression", "sgd_regressor"), key=lambda k: scores[k]["rmse"]
    )
    return pipelines, scores, histories, trials, best, selected


def main():
    cfg = config()
    frozen_path = RESULTS / "frozen_manifest.json"
    candidate_path = ROOT / "models/candidates.joblib"
    cached = False
    if frozen_path.exists():
        frozen = read_json(frozen_path)
        if frozen["config_sha256"] != checksum(ROOT / "config/project_config.json"):
            raise RuntimeError(
                "Config changed after test publication; tuning on exposed test is forbidden."
            )
        if candidate_path.exists():
            if checksum(candidate_path) != frozen["candidate_sha256"]:
                raise RuntimeError(
                    "Candidate checksum mismatch; do not publish an altered model."
                )
            metadata = read_json(RESULTS / "model_metadata.json")
            if metadata.get("fit_scope") == "train only":
                if (
                    checksum(ROOT / "models/final_pipeline.joblib")
                    != frozen["serving_model_sha256"]
                ):
                    raise RuntimeError("Serving artifact checksum mismatch.")
                print(
                    "Frozen train-only pipeline verified. No retraining or test evaluation."
                )
                return
            cached = True
    frame = load_california_housing()
    ids = persist_split()
    train, val = frame.iloc[ids["train"]], frame.iloc[ids["validation"]]
    if cached:
        # Sửa phạm vi serving bằng candidate đã chọn, không fit lại hoặc đổi model theo test.
        pipelines = joblib.load(candidate_path)
        scores = read_json(RESULTS / "validation_metrics.json")
        histories = read_json(RESULTS / "sgd_history.json")
        trials = read_json(RESULTS / "sgd_trials.json")
        best = min(trials, key=lambda k: trials[k]["rmse"])
        selected = min(
            ("linear_regression", "sgd_regressor"), key=lambda k: scores[k]["rmse"]
        )
    else:
        pipelines, scores, histories, trials, best, selected = fit_candidates(
            train, val, cfg
        )
    original = read_json(ROOT / "reports/archive/initial/metrics.json")
    # Kiểm tra validation với lần chạy gốc; không dùng test để lựa chọn.
    for name in scores:
        np.testing.assert_allclose(
            list(scores[name].values()),
            list(original["validation"][name].values()),
            rtol=1e-8,
            atol=1e-10,
        )
    if selected != original["selection"]["selected_model"]:
        raise RuntimeError("Model selection differs from the frozen experiment.")
    scaler = pipelines[selected].named_steps["scaler"]
    np.testing.assert_allclose(scaler.mean_, train[EXPECTED_FEATURES].mean())
    if scaler.n_samples_seen_ != len(train):
        raise RuntimeError("Selected scaler must fit train only.")
    (ROOT / "models").mkdir(exist_ok=True)
    if not cached:
        joblib.dump(pipelines, candidate_path)
    joblib.dump(pipelines[selected], ROOT / "models/final_pipeline.joblib")
    save_json(RESULTS / "validation_metrics.json", scores)
    save_json(RESULTS / "sgd_history.json", histories)
    save_json(RESULTS / "sgd_trials.json", trials)
    save_json(
        RESULTS / "coefficients.json",
        [
            {"feature": n, "standardized_coefficient": float(v)}
            for n, v in zip(
                EXPECTED_FEATURES,
                pipelines["linear_regression"].named_steps["model"].coef_,
            )
        ],
    )
    save_json(
        RESULTS / "input_schema.json",
        {
            n: {
                "min": float(train[n].min()),
                "max": float(train[n].max()),
                "median": float(train[n].median()),
            }
            for n in EXPECTED_FEATURES
        },
    )
    decision = {
        "selection_metric": "validation RMSE",
        "selected_model": selected,
        "selected_sgd_learning_rate": float(best),
        "test_was_not_used_for_selection": True,
        "candidate_fit_scope": "train only",
        "serving_fit_scope": "train only",
        "refit_policy": "Publish the already selected train-only candidate; never refit on validation/test.",
    }
    save_json(RESULTS / "model_selection.json", decision)
    frozen = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "config_sha256": checksum(ROOT / "config/project_config.json"),
        "split_sha256": checksum(ROOT / "data/splits.json"),
        "candidate_sha256": checksum(ROOT / "models/candidates.joblib"),
        "selected_model": selected,
        "serving_model_sha256": checksum(ROOT / "models/final_pipeline.joblib"),
        "test_already_observed": True,
        "evaluation_policy": "Reuse initial final-test metrics; additional residuals are a post-hoc audit, not an independent test.",
    }
    save_json(frozen_path, frozen)
    save_json(
        RESULTS / "model_metadata.json",
        {
            "model_name": "California Housing Linear Study",
            "selected_model": selected,
            "features": EXPECTED_FEATURES,
            "target": TARGET,
            "target_unit": "100,000 USD",
            "random_state": cfg["random_state"],
            "python_version": platform.python_version(),
            "scikit_learn_version": sklearn.__version__,
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
            "fit_scope": decision["serving_fit_scope"],
            "model_sha256": frozen["serving_model_sha256"],
        },
    )
    # Chỉ ánh xạ score đã công bố của candidate được chọn. Không đọc test ở đây.
    active_metrics = json.loads(json.dumps(original))
    active_metrics["test"]["selected_pipeline"] = original["test"][selected]
    active_metrics["selection"] = decision
    save_json(RESULTS / "metrics.json", active_metrics)
    save_json(
        RESULTS / "pipeline_audit.json",
        {
            "reason": "Correct serving fit scope to the train-only candidate selected by validation.",
            "model_selection_unchanged": True,
            "new_fit_on_validation_or_test": False,
            "test_metrics_source": f"reports/archive/initial/metrics.json -> test.{selected}",
            "legacy_artifact": "reports/archive/initial/final_pipeline.joblib",
            "legacy_fit_scope": "train + validation (including scaler)",
            "current_fit_scope": "train only",
            "train_samples": len(train),
            "test_already_observed": True,
            "note": "A compliance correction, not a new independently evaluated experiment.",
        },
    )
    print(
        json.dumps(
            {"selected": selected, "best_learning_rate": best, "validation": scores},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
