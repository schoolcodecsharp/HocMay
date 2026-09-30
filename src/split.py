"""Split cố định trước mọi thao tác học; ID chỉ phục vụ truy nguyên."""

import numpy as np
from sklearn.model_selection import train_test_split
from src.common import ROOT, config, save_json


def split_ids(count=20640):
    cfg = config()
    if not np.isclose(
        sum(cfg[k] for k in ("train_size", "validation_size", "test_size")), 1
    ):
        raise ValueError("Tổng tỷ lệ split phải bằng 1.")
    train, rest = train_test_split(
        np.arange(count),
        test_size=cfg["validation_size"] + cfg["test_size"],
        random_state=cfg["random_state"],
    )
    val, test = train_test_split(
        rest,
        test_size=cfg["test_size"] / (cfg["validation_size"] + cfg["test_size"]),
        random_state=cfg["random_state"],
    )
    return {"train": train.tolist(), "validation": val.tolist(), "test": test.tolist()}


def persist_split():
    result = split_ids()
    save_json(
        ROOT / "data/splits.json",
        {"random_state": config()["random_state"], "indices": result},
    )
    return result


if __name__ == "__main__":
    print({k: len(v) for k, v in persist_split().items()})
