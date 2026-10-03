"""Chất lượng và EDA trên train; không sửa/xóa/cắt ngọn dòng nào."""

import os
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".cache/matplotlib")
)
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from src.common import RESULTS, FIGURES, save_json
from src.data import load_california_housing, EXPECTED_FEATURES, TARGET
from src.split import persist_split

UNITS = {
    "MedInc": "10,000 USD",
    "HouseAge": "years",
    "AveRooms": "rooms/household",
    "AveBedrms": "bedrooms/household",
    "Population": "people",
    "AveOccup": "people/household",
    "Latitude": "degrees",
    "Longitude": "degrees",
    "MedHouseVal": "100,000 USD",
}


def save_figure(fig, name):
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES / name, dpi=160, bbox_inches="tight")
    plt.close(fig)


def main():
    frame = load_california_housing()
    ids = persist_split()
    train = frame.iloc[ids["train"]]
    q1, q3 = train.quantile(0.25), train.quantile(0.75)
    iqr = q3 - q1
    outliers = ((train < q1 - 1.5 * iqr) | (train > q3 + 1.5 * iqr)).sum()
    quality = {
        "samples": len(frame),
        "features": len(EXPECTED_FEATURES),
        "columns": {k: str(v) for k, v in frame.dtypes.items()},
        "audit_scope": "train only except dataset shape/schema",
        "missing_values": train.isna().sum().astype(int).to_dict(),
        "duplicate_rows": int(train.duplicated().sum()),
        "removed_rows": 0,
        "removed_rows_reason": "Không loại dòng nào; outlier là cờ kiểm tra, không tự động xóa.",
        "target_cap_count_train": int((train[TARGET] >= 5).sum()),
        "target_max_train": float(train[TARGET].max()),
        "iqr_outliers_train": outliers.astype(int).to_dict(),
        "split": {k: len(v) for k, v in ids.items()},
        "descriptive_statistics_train": train.describe().to_dict(),
    }
    save_json(RESULTS / "data_quality.json", quality)
    train.describe().to_csv(RESULTS / "train_statistics.csv")
    corr = train.corr()
    corr.to_csv(RESULTS / "train_correlations.csv")
    fig, axes = plt.subplots(3, 3, figsize=(13, 10))
    for ax, name in zip(axes.flat, train.columns):
        ax.hist(train[name], bins=40, color="#173f4a")
        ax.set(
            title=f"Train: {name}",
            xlabel=f"{name} ({UNITS[name]})",
            ylabel="Block groups",
        )
    save_figure(fig, "eda_distributions.png")
    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(corr, vmin=-1, vmax=1, cmap="coolwarm")
    ax.set_xticks(range(9), corr.columns, rotation=60, ha="right")
    ax.set_yticks(range(9), corr.columns)
    for i in range(9):
        for j in range(9):
            ax.text(j, i, f"{corr.iloc[i,j]:.2f}", ha="center", va="center", fontsize=8)
    ax.set_title("Pearson correlation - train only")
    fig.colorbar(im, ax=ax)
    save_figure(fig, "eda_correlations.png")
    fig, axes = plt.subplots(2, 3, figsize=(13, 8))
    for ax, name in zip(
        axes.flat,
        ["MedInc", "HouseAge", "AveRooms", "Population", "AveOccup", "AveBedrms"],
    ):
        ax.scatter(train[name], train[TARGET], s=3, alpha=0.15, color="#173f4a")
        ax.set(
            title=f"{name} vs target (train)",
            xlabel=f"{name} ({UNITS[name]})",
            ylabel="MedHouseVal (100,000 USD)",
        )
        if name in ("AveRooms", "Population", "AveOccup", "AveBedrms"):
            ax.set_xscale("log")
    save_figure(fig, "eda_relationships.png")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].hist(train[TARGET], bins=50, color="#173f4a")
    axes[0].axvline(5, color="#bb583b")
    axes[0].set(
        title="Target distribution - TRAIN",
        xlabel="MedHouseVal (100,000 USD)",
        ylabel="Block groups",
    )
    im = axes[1].scatter(
        train.Longitude, train.Latitude, c=train[TARGET], s=3, alpha=0.6, cmap="viridis"
    )
    axes[1].set(
        title="California - TRAIN",
        xlabel="Longitude (degrees)",
        ylabel="Latitude (degrees)",
    )
    fig.colorbar(im, ax=axes[1], label="MedHouseVal (100,000 USD)")
    save_figure(fig, "eda_target_geography.png")
    print("Train EDA complete:", len(train), "rows; no rows removed.")


if __name__ == "__main__":
    main()
