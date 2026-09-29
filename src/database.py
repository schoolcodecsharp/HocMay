"""Nhập cadata.txt vào SQLite và xác minh toàn bộ giá trị với scikit-learn."""

import argparse
import io
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
from src.common import ROOT, RESULTS, checksum, save_json
from src.data import EXPECTED_FEATURES, TARGET, load_california_housing
from src.split import persist_split, split_ids

DB_PATH = ROOT / "data/california_housing.sqlite3"
RAW_COLUMNS = [
    "median_value_usd",
    "median_income",
    "housing_age",
    "total_rooms",
    "total_bedrooms",
    "population",
    "households",
    "latitude",
    "longitude",
]


def read_cadata(path):
    # Header gồm mô tả/bảng nghiên cứu; bắt đầu ở dòng có đúng 9 số.
    lines = Path(path).read_text(encoding="latin-1").splitlines()
    start = None
    for i, line in enumerate(lines):
        fields = line.split()
        if len(fields) != 9:
            continue
        try:
            [float(v) for v in fields]
            start = i
            break
        except ValueError:
            continue
    if start is None:
        raise ValueError("Không tìm thấy bảng 9 cột trong cadata.txt.")
    values = np.loadtxt(io.StringIO("\n".join(lines[start:])))
    if values.shape != (20640, 9) or not np.isfinite(values).all():
        raise ValueError("cadata.txt phải có 20.640 dòng, 9 cột số hữu hạn.")
    if (values[:, :7] <= 0).any():
        raise ValueError(
            "Giá trị, thu nhập, tuổi, số phòng, dân số và số hộ phải dương."
        )
    return pd.DataFrame(values, columns=RAW_COLUMNS)


def to_features(raw):
    return pd.DataFrame(
        {
            "MedInc": raw.median_income,
            "HouseAge": raw.housing_age,
            "AveRooms": raw.total_rooms / raw.households,
            "AveBedrms": raw.total_bedrooms / raw.households,
            "Population": raw.population,
            "AveOccup": raw.population / raw.households,
            "Latitude": raw.latitude,
            "Longitude": raw.longitude,
            "MedHouseVal": raw.median_value_usd / 100000,
        }
    )


def build_database(source=ROOT / "houses/cadata.txt", destination=DB_PATH):
    source, destination = Path(source), Path(destination)
    if destination.exists():
        with sqlite3.connect(destination) as conn:
            previous = dict(conn.execute("SELECT key,value FROM source_metadata"))
            count = conn.execute("SELECT count(*) FROM block_groups").fetchone()[0]
            if (
                conn.execute("PRAGMA integrity_check").fetchone()[0] != "ok"
                or conn.execute("PRAGMA foreign_key_check").fetchall()
            ):
                raise ValueError("CSDL không toàn vẹn; dùng --output khác để nhập lại.")
            actual_splits = dict(
                conn.execute("SELECT row_id,split FROM split_membership")
            )
            expected_splits = {
                i: name for name, ids in split_ids().items() for i in ids
            }
            if actual_splits != expected_splits:
                raise ValueError(
                    "Split trong CSDL khác config; không ghi đè dữ liệu cũ."
                )
        if previous.get("source_sha256") == checksum(source) and count == 20640:
            print("Database already imported; original rows preserved.")
            return previous
        raise FileExistsError(
            "CSDL đã tồn tại với nguồn khác; chọn --output khác để bảo toàn dữ liệu."
        )
    raw = read_cadata(source)
    reference = load_california_housing()
    derived = to_features(raw)
    np.testing.assert_allclose(derived, reference, rtol=0, atol=1e-12)
    splits = persist_split()
    manifest = {
        "source_file": source.name,
        "source_sha256": checksum(source),
        "imported_at_utc": datetime.now(timezone.utc).isoformat(),
        "rows": 20640,
        "raw_columns": RAW_COLUMNS,
        "verified_against": "fetch_california_housing(as_frame=True)",
        "max_absolute_difference": float(
            np.max(np.abs(derived.to_numpy() - reference.to_numpy()))
        ),
        "removed_rows": 0,
        "schema_version": 1,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(destination) as conn:
        conn.executescript((ROOT / "data/schema.sql").read_text(encoding="utf-8"))
        with conn:
            conn.executemany(
                "INSERT INTO block_groups VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    (i, *row)
                    for i, row in enumerate(raw.itertuples(index=False, name=None))
                ),
            )
            conn.executemany(
                "INSERT INTO split_membership VALUES (?,?)",
                ((i, name) for name, ids in splits.items() for i in ids),
            )
            conn.executemany(
                "INSERT INTO source_metadata VALUES (?,?)",
                (
                    (
                        k,
                        (
                            json.dumps(v, ensure_ascii=False)
                            if not isinstance(v, str)
                            else v
                        ),
                    )
                    for k, v in manifest.items()
                ),
            )
        if conn.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("SQLite integrity check failed.")
    save_json(RESULTS / "database_manifest.json", manifest)
    return manifest


def read_split(name, path=DB_PATH):
    if name not in ("train", "validation", "test"):
        raise ValueError("Unknown split")
    with sqlite3.connect(f"{Path(path).resolve().as_uri()}?mode=ro", uri=True) as conn:
        frame = pd.read_sql_query(
            "SELECT * FROM housing_features WHERE split=? ORDER BY row_id",
            conn,
            params=[name],
        )
    return frame.set_index("row_id")[EXPECTED_FEATURES + [TARGET]]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "houses/cadata.txt")
    parser.add_argument("--output", type=Path, default=DB_PATH)
    args = parser.parse_args()
    print(json.dumps(build_database(args.source, args.output), indent=2))
