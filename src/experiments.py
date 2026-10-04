"""Bốn thí nghiệm, bảng phân tích lỗi và figures từ artifact thực tế."""

import numpy as np
import pandas as pd
from src.common import RESULTS, FIGURES, read_json, save_json
from src.eda import plt, save_figure


def main():
    metrics = read_json(RESULTS / "metrics.json")
    histories = read_json(RESULTS / "sgd_history.json")
    trials = read_json(RESULTS / "sgd_trials.json")
    coefs = read_json(RESULTS / "coefficients.json")
    names = ["mean_baseline", "linear_regression", "sgd_regressor"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, key in zip(axes, ["mae", "rmse", "r2"]):
        ax.bar(
            ["Mean", "Linear", "SGD"],
            [metrics["validation"][n][key] for n in names],
            color=["#aaa090", "#173f4a", "#bb583b"],
        )
        ax.set(
            title=f"Validation {key.upper()}",
            ylabel="Score" if key == "r2" else "100,000 USD",
        )
    save_figure(fig, "validation_comparison.png")
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, key in zip(axes, ["mae", "rmse", "r2"]):
        ax.bar(
            ["Mean", "Linear", "SGD"],
            [metrics["test"][n][key] for n in names],
            color=["#aaa090", "#173f4a", "#bb583b"],
        )
        ax.set(
            title=f"Frozen test {key.upper()}",
            ylabel="Score" if key == "r2" else "100,000 USD",
        )
    save_figure(fig, "model_comparison.png")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(
        [r["feature"] for r in coefs],
        [r["standardized_coefficient"] for r in coefs],
        color="#173f4a",
    )
    ax.axvline(0, color="black", lw=1)
    ax.set(
        title="Linear Regression - train-only coefficients",
        xlabel="Coefficient (100,000 USD per train standard deviation)",
    )
    save_figure(fig, "standardized_coefficients.png")
    fig, ax = plt.subplots(figsize=(10, 5))
    for rate, history in histories.items():
        ax.plot(
            [r["epoch"] for r in history],
            [r["train_loss"] for r in history],
            label=f"eta={rate}",
        )
    ax.set(
        xlabel="Epoch",
        ylabel="0.5 x MSE (symlog)",
        title="SGD training loss - same train split",
    )
    ax.set_yscale("symlog", linthresh=0.1)
    ax.legend()
    save_figure(fig, "sgd_learning_curves.png")
    residual = pd.read_csv(RESULTS / "residual_rows.csv")
    cap = residual.MedHouseVal >= 5
    save_json(
        RESULTS / "residual_analysis.json",
        {
            "definition": "residual = y_true - y_pred",
            "mean_residual": float(residual.residual.mean()),
            "target_cap_test_samples": int(cap.sum()),
            "mean_residual_at_cap": float(residual.loc[cap, "residual"].mean()),
            "fit_scope": "train only",
            "analysis_kind": "post-hoc verification, no tuning",
        },
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    for flag, label, color in [
        (False, "Below cap", "#173f4a"),
        (True, "At target cap", "#bb583b"),
    ]:
        rows = residual.loc[cap == flag]
        ax.scatter(
            rows.predicted, rows.residual, s=9, alpha=0.4, color=color, label=label
        )
    ax.axhline(0, color="black", lw=1)
    ax.legend()
    ax.set(
        title="Residual vs predicted - frozen train-only LR",
        xlabel="Predicted (100,000 USD)",
        ylabel="Residual (100,000 USD)",
    )
    save_figure(fig, "residual_vs_predicted.png")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(residual.residual, bins=50, color="#173f4a")
    ax.axvline(0, color="#bb583b")
    ax.set(
        title="Residual distribution - frozen train-only LR",
        xlabel="Residual (100,000 USD)",
        ylabel="Block groups",
    )
    save_figure(fig, "residual_distribution.png")
    residual["price_band"] = pd.cut(
        residual.MedHouseVal, [0, 1, 2, 3, 4, 5, 6], right=False
    )
    residual["latitude_band"] = pd.cut(residual.Latitude, [32, 35, 38, 43], right=False)

    def summary(group):
        return {
            "count": len(group),
            "mean_residual": float(group.residual.mean()),
            "mae": float(group.residual.abs().mean()),
            "rmse": float(np.sqrt((group.residual**2).mean())),
        }

    by_price = {
        str(k): summary(g) for k, g in residual.groupby("price_band", observed=True)
    }
    by_geo = {
        str(k): summary(g) for k, g in residual.groupby("latitude_band", observed=True)
    }
    save_json(
        RESULTS / "residual_groups.json",
        {
            "by_actual_price": by_price,
            "by_latitude": by_geo,
            "geographic_groups": "Latitude bands, descriptive only; no causal interpretation.",
        },
    )
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    cap = residual.MedHouseVal >= 5
    axes[0].scatter(
        residual.MedHouseVal,
        residual.residual,
        c=np.where(cap, "#bb583b", "#173f4a"),
        s=5,
        alpha=0.4,
    )
    axes[0].axhline(0, color="black", lw=1)
    axes[0].set(
        title="Residual by actual price",
        xlabel="Actual MedHouseVal (100,000 USD)",
        ylabel="Residual (100,000 USD)",
    )
    im = axes[1].scatter(
        residual.Longitude,
        residual.Latitude,
        c=residual.residual,
        cmap="coolwarm",
        s=7,
        vmin=-2,
        vmax=2,
    )
    axes[1].set(
        title="Residual by location",
        xlabel="Longitude (degrees)",
        ylabel="Latitude (degrees)",
    )
    fig.colorbar(im, ax=axes[1], label="Residual (100,000 USD)")
    save_figure(fig, "residual_price_geography.png")
    experiment = {
        "comparison_validation": metrics["validation"],
        "sgd_trials": trials,
        "sgd_first_last": {
            k: {"first": v[0]["train_loss"], "last": v[-1]["train_loss"]}
            for k, v in histories.items()
        },
        "coefficients": coefs,
        "residual_groups": by_price,
        "test_policy": "Previously published metrics preserved; residuals are a post-hoc audit.",
    }
    save_json(RESULTS / "experiments.json", experiment)
    print("Experiments and residual groups generated from real artifacts.")


if __name__ == "__main__":
    main()
