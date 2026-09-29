"""Tải và kiểm tra bộ dữ liệu California Housing từ scikit-learn."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import sklearn
from sklearn.datasets import fetch_california_housing


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "raw" / "california_housing.csv"
DEFAULT_METADATA = PROJECT_ROOT / "data" / "raw" / "california_housing_metadata.json"
DATA_CACHE = PROJECT_ROOT / ".cache" / "scikit_learn_data"

EXPECTED_FEATURES = [
    "MedInc",
    "HouseAge",
    "AveRooms",
    "AveBedrms",
    "Population",
    "AveOccup",
    "Latitude",
    "Longitude",
]
TARGET = "MedHouseVal"


def load_california_housing() -> pd.DataFrame:
    """Tải dataset chính thức và trả về DataFrame gồm 8 feature + target."""
    # Đặt cache trong project để không phụ thuộc thư mục người dùng của từng máy.
    dataset = fetch_california_housing(as_frame=True, data_home=DATA_CACHE)
    frame = dataset.frame.copy()

    expected_columns = EXPECTED_FEATURES + [TARGET]
    if frame.columns.tolist() != expected_columns:
        raise ValueError(
            "Schema dataset không đúng như mong đợi. "
            f"Nhận được: {frame.columns.tolist()}"
        )
    if frame.shape != (20_640, 9):
        raise ValueError(f"Kích thước dataset không đúng: {frame.shape}")

    return frame


def sha256_file(path: Path) -> str:
    """Tính SHA-256 cho file CSV đã tạo để kiểm tra khả năng tái lập."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_dataset(output_path: Path, metadata_path: Path) -> None:
    """Tải, kiểm tra và lưu dữ liệu cùng metadata."""
    frame = load_california_housing()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)

    metadata = {
        "dataset": "California Housing",
        "source": "scikit-learn fetch_california_housing(as_frame=True)",
        "source_url": (
            "https://scikit-learn.org/stable/modules/generated/"
            "sklearn.datasets.fetch_california_housing.html"
        ),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "rows": int(frame.shape[0]),
        "features": EXPECTED_FEATURES,
        "target": TARGET,
        "target_unit": "100,000 USD",
        "columns": frame.columns.tolist(),
        "python_version": platform.python_version(),
        "scikit_learn_version": sklearn.__version__,
        "pandas_version": pd.__version__,
        "csv_sha256": sha256_file(output_path),
    }
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Dùng thông báo ASCII để chạy ổn định trên terminal Windows mọi encoding.
    print(f"Saved dataset: {output_path}")
    print(f"Saved metadata: {metadata_path}")
    print(f"Shape: {frame.shape[0]} rows x {frame.shape[1]} columns")
    print(f"Missing values: {int(frame.isna().sum().sum())}")
    print(f"SHA-256: {metadata['csv_sha256']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    save_dataset(args.output, args.metadata)
