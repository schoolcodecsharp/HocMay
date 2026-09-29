"""Đường dẫn, config và JSON dùng chung; không phụ thuộc thư mục chạy lệnh."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "reports" / "results"
FIGURES = ROOT / "reports" / "figures"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def config():
    return read_json(ROOT / "config/project_config.json")


def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
