"""Hiển thị kết quả đánh giá đã được sinh bởi quy trình train đã đóng băng."""

from __future__ import annotations

import json
from pathlib import Path


RESULT_PATH = Path(__file__).resolve().parents[1] / "reports" / "results" / "metrics.json"


def main() -> None:
    if not RESULT_PATH.exists():
        raise FileNotFoundError("Chưa có kết quả. Hãy chạy: python -m src.train")
    print(json.dumps(json.loads(RESULT_PATH.read_text(encoding="utf-8")), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
