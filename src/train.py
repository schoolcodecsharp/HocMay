"""Huấn luyện, chọn mô hình bằng validation và đánh giá test đúng một lần."""

from __future__ import annotations

import json
import os
import platform
from pathlib import Path

import joblib
# Giữ cache matplotlib trong project, không phụ thuộc thư mục người dùng.
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".cache" / "matplotlib"))
import matplotlib
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.data import EXPECTED_FEATURES, TARGET, load_california_housing
from src.metrics import regression_metrics


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "project_config.json"
RESULTS_DIR = ROOT / "reports" / "results"
FIGURES_DIR = ROOT / "reports" / "figures"
MODEL_PATH = ROOT / "models" / "final_pipeline.joblib"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def split_data(frame: pd.DataFrame, config: dict):
    """Split trước mọi preprocessing; validation và test đều chiếm 15%."""
    x = frame[EXPECTED_FEATURES]
    y = frame[TARGET]
    x_train, x_temp, y_train, y_temp = train_test_split(
        x,
        y,
        test_size=config["validation_size"] + config["test_size"],
        random_state=config["random_state"],
    )
    relative_test_size = config["test_size"] / (
        config["validation_size"] + config["test_size"]
    )
    x_val, x_test, y_val, y_test = train_test_split(
        x_temp,
        y_temp,
        test_size=relative_test_size,
        random_state=config["random_state"],
    )
    return x_train, x_val, x_test, y_train, y_val, y_test


def train_sgd_candidates(x_train, y_train, x_val, y_val, config):
    """Theo dõi loss thật sau từng epoch cho mỗi learning rate."""
    scaler = StandardScaler().fit(x_train)
    x_train_scaled = scaler.transform(x_train)
    x_val_scaled = scaler.transform(x_val)
    candidates = {}

    for learning_rate in config["sgd_learning_rates"]:
        model = SGDRegressor(
            loss="squared_error",
            penalty=None,
            learning_rate="constant",
            eta0=learning_rate,
            max_iter=1,
            tol=None,
            warm_start=True,
            shuffle=False,
            random_state=config["random_state"],
        )
        history = []
        rng = np.random.default_rng(config["random_state"])
        for epoch in range(1, config["sgd_epochs"] + 1):
            order = rng.permutation(len(x_train_scaled))
            model.partial_fit(x_train_scaled[order], y_train.iloc[order])
            train_pred = model.predict(x_train_scaled)
            # Squared-error loss của SGDRegressor là 0.5 * mean squared error.
            loss = 0.5 * float(np.mean((y_train.to_numpy() - train_pred) ** 2))
            history.append({"epoch": epoch, "train_loss": loss})

        val_pred = model.predict(x_val_scaled)
        candidates[str(learning_rate)] = {
            "pipeline": Pipeline([("scaler", scaler), ("model", model)]),
            "history": history,
            "validation_metrics": regression_metrics(y_val.to_numpy(), val_pred),
        }
    return candidates


def save_json(path: Path, value: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def create_figures(
    frame,
    results,
    histories,
    linear_pipeline,
    x_test,
    y_test,
    final_test_pred,
):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")

    # 1. So sánh model bằng các metric thực tế.
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    names = ["Mean baseline", "Linear Regression", "SGDRegressor"]
    colors = ["#9b8d7a", "#153c4a", "#c65d3b"]
    for axis, metric, title in zip(axes, ["mae", "rmse", "r2"], ["MAE", "RMSE", "R²"]):
        values = [results["test"][name][metric] for name in ["mean_baseline", "linear_regression", "sgd_regressor"]]
        axis.bar(names, values, color=colors)
        axis.set_title(title)
        axis.tick_params(axis="x", rotation=25)
        axis.set_ylabel("Đơn vị target" if metric != "r2" else "Điểm")
    fig.suptitle("So sánh mô hình trên final test")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "model_comparison.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    # 2. Loss curve từ quá trình SGD thực tế.
    fig, axis = plt.subplots(figsize=(9, 5))
    for learning_rate, history in histories.items():
        axis.plot([row["epoch"] for row in history], [row["train_loss"] for row in history], label=f"η = {learning_rate}")
    axis.set_title("SGD learning curves")
    axis.set_xlabel("Epoch")
    axis.set_ylabel("Training loss = 0.5 × MSE")
    axis.set_yscale("symlog", linthresh=0.1)
    axis.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "sgd_learning_curves.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    # 3. Standardized coefficients của Linear Regression.
    coefficients = linear_pipeline.named_steps["model"].coef_
    order = np.argsort(np.abs(coefficients))
    fig, axis = plt.subplots(figsize=(8, 5))
    axis.barh(np.array(EXPECTED_FEATURES)[order], coefficients[order], color=np.where(coefficients[order] >= 0, "#c65d3b", "#153c4a"))
    axis.axvline(0, color="#202b2f", linewidth=1)
    axis.set_title("Hệ số Linear Regression sau chuẩn hóa")
    axis.set_xlabel("Standardized coefficient — mối liên hệ, không phải nhân quả")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "standardized_coefficients.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    residuals = y_test.to_numpy() - final_test_pred
    # 4. Residual vs predicted.
    fig, axis = plt.subplots(figsize=(8, 5))
    cap_mask = y_test.to_numpy() >= 5.0
    axis.scatter(final_test_pred[~cap_mask], residuals[~cap_mask], s=10, alpha=0.35, color="#153c4a", label="Target < 5.0")
    axis.scatter(final_test_pred[cap_mask], residuals[cap_mask], s=16, alpha=0.7, color="#c65d3b", label="Target ≥ 5.0")
    axis.axhline(0, color="#202b2f", linewidth=1)
    axis.set_title("Residual theo giá trị dự đoán — final test")
    axis.set_xlabel("Predicted MedHouseVal (× 100.000 USD)")
    axis.set_ylabel("Residual = y_true − y_pred")
    axis.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "residual_vs_predicted.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    # 5. Phân phối residual.
    fig, axis = plt.subplots(figsize=(8, 5))
    axis.hist(residuals, bins=45, color="#153c4a", alpha=0.88)
    axis.axvline(0, color="#c65d3b", linewidth=2)
    axis.set_title("Phân phối residual — final test")
    axis.set_xlabel("Residual (× 100.000 USD)")
    axis.set_ylabel("Số census block group")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "residual_distribution.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    # 6. Hai hình EDA mô tả target và không gian; không dùng để tuning.
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].hist(frame[TARGET], bins=50, color="#153c4a")
    axes[0].axvline(5.0, color="#c65d3b", linewidth=2, label="Target cap gần 5.0")
    axes[0].set_title("Phân phối MedHouseVal")
    axes[0].set_xlabel("MedHouseVal (× 100.000 USD)")
    axes[0].set_ylabel("Số block group")
    axes[0].legend()
    scatter = axes[1].scatter(frame["Longitude"], frame["Latitude"], c=frame[TARGET], s=3, cmap="viridis", alpha=0.55)
    axes[1].set_title("Phân bố không gian của target")
    axes[1].set_xlabel("Longitude")
    axes[1].set_ylabel("Latitude")
    fig.colorbar(scatter, ax=axes[1], label="MedHouseVal")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "eda_target_geography.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    config = load_config()
    frame = load_california_housing()
    x_train, x_val, x_test, y_train, y_val, y_test = split_data(frame, config)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    data_quality = {
        "samples": int(frame.shape[0]),
        "features": len(EXPECTED_FEATURES),
        "columns": {name: str(dtype) for name, dtype in frame.dtypes.items()},
        "missing_values": {name: int(value) for name, value in frame.isna().sum().items()},
        "duplicate_rows": int(frame.duplicated().sum()),
        "removed_rows": 0,
        "removed_rows_reason": "Không loại dòng nào.",
        "target_cap_count": int((frame[TARGET] >= 5.0).sum()),
        "split": {"train": len(x_train), "validation": len(x_val), "test": len(x_test)},
    }
    save_json(RESULTS_DIR / "data_quality.json", data_quality)

    mean_value = float(y_train.mean())
    baseline_val_pred = np.full(len(y_val), mean_value)

    linear_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LinearRegression()),
    ])
    linear_pipeline.fit(x_train, y_train)
    linear_val_pred = linear_pipeline.predict(x_val)

    sgd_candidates = train_sgd_candidates(x_train, y_train, x_val, y_val, config)
    best_lr = min(
        sgd_candidates,
        key=lambda rate: sgd_candidates[rate]["validation_metrics"]["rmse"],
    )
    best_sgd_pipeline = sgd_candidates[best_lr]["pipeline"]

    validation = {
        "mean_baseline": regression_metrics(y_val.to_numpy(), baseline_val_pred),
        "linear_regression": regression_metrics(y_val.to_numpy(), linear_val_pred),
        "sgd_regressor": sgd_candidates[best_lr]["validation_metrics"],
    }
    selected_model = min(
        ["linear_regression", "sgd_regressor"],
        key=lambda name: validation[name]["rmse"],
    )

    # Quyết định đã đóng băng tại đây, trước khi test được dùng.
    decision = {
        "selection_metric": "validation RMSE",
        "selected_model": selected_model,
        "selected_sgd_learning_rate": float(best_lr),
        "test_was_not_used_for_selection": True,
    }
    save_json(RESULTS_DIR / "model_selection.json", decision)

    # Refit model đã chọn trên train + validation trước final test.
    x_train_val = pd.concat([x_train, x_val], axis=0)
    y_train_val = pd.concat([y_train, y_val], axis=0)
    if selected_model == "linear_regression":
        final_pipeline = clone(linear_pipeline).fit(x_train_val, y_train_val)
    else:
        final_pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("model", SGDRegressor(
                loss="squared_error",
                penalty=None,
                learning_rate="constant",
                eta0=float(best_lr),
                max_iter=config["sgd_epochs"],
                tol=None,
                random_state=config["random_state"],
            )),
        ]).fit(x_train_val, y_train_val)

    # Final test block: mọi model được đánh giá một lần sau khi quyết định đã freeze.
    baseline_test_pred = np.full(len(y_test), mean_value)
    linear_test_pred = linear_pipeline.predict(x_test)
    sgd_test_pred = best_sgd_pipeline.predict(x_test)
    final_test_pred = final_pipeline.predict(x_test)
    test = {
        "mean_baseline": regression_metrics(y_test.to_numpy(), baseline_test_pred),
        "linear_regression": regression_metrics(y_test.to_numpy(), linear_test_pred),
        "sgd_regressor": regression_metrics(y_test.to_numpy(), sgd_test_pred),
        "selected_pipeline": regression_metrics(y_test.to_numpy(), final_test_pred),
    }

    results = {"validation": validation, "test": test, "selection": decision}
    save_json(RESULTS_DIR / "metrics.json", results)
    histories = {rate: item["history"] for rate, item in sgd_candidates.items()}
    save_json(RESULTS_DIR / "sgd_history.json", histories)

    coefficients = [
        {"feature": feature, "standardized_coefficient": float(coef)}
        for feature, coef in zip(EXPECTED_FEATURES, linear_pipeline.named_steps["model"].coef_)
    ]
    save_json(RESULTS_DIR / "coefficients.json", coefficients)

    input_schema = {
        feature: {
            "min": float(x_train_val[feature].min()),
            "max": float(x_train_val[feature].max()),
            "median": float(x_train_val[feature].median()),
        }
        for feature in EXPECTED_FEATURES
    }
    save_json(RESULTS_DIR / "input_schema.json", input_schema)

    cap_mask = y_test.to_numpy() >= 5.0
    residual_analysis = {
        "definition": "residual = y_true - y_pred",
        "mean_residual": float(np.mean(y_test.to_numpy() - final_test_pred)),
        "target_cap_test_samples": int(cap_mask.sum()),
        "mean_residual_at_cap": float(np.mean((y_test.to_numpy() - final_test_pred)[cap_mask])),
    }
    save_json(RESULTS_DIR / "residual_analysis.json", residual_analysis)

    metadata = {
        "model_name": "California Housing Linear Study",
        "selected_model": selected_model,
        "features": EXPECTED_FEATURES,
        "target": TARGET,
        "target_unit": "100,000 USD",
        "random_state": config["random_state"],
        "python_version": platform.python_version(),
        "scikit_learn_version": sklearn.__version__,
        "pandas_version": pd.__version__,
        "numpy_version": np.__version__,
    }
    save_json(RESULTS_DIR / "model_metadata.json", metadata)
    joblib.dump(final_pipeline, MODEL_PATH)

    create_figures(frame, results, histories, linear_pipeline, x_test, y_test, final_test_pred)
    print(f"Selected model: {selected_model}")
    print(f"Best SGD learning rate: {best_lr}")
    print(f"Model saved: {MODEL_PATH}")
    print(json.dumps(test["selected_pipeline"], indent=2))


if __name__ == "__main__":
    main()
