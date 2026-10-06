"""Nạp artifact và thực hiện prediction; không huấn luyện trong web request."""

from __future__ import annotations

import json
import math
import hashlib
from threading import Lock
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "final_pipeline.joblib"
SCHEMA_PATH = ROOT / "reports" / "results" / "input_schema.json"
METADATA_PATH = ROOT / "reports" / "results" / "model_metadata.json"


class ModelService:
    def __init__(self, model_path: Path = MODEL_PATH):
        self.model_path = model_path
        self.pipeline = None
        self.schema = None
        self.metadata = None
        self.lock = Lock()

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Không tìm thấy model artifact: {self.model_path}")
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        if hashlib.sha256(self.model_path.read_bytes()).hexdigest() != metadata.get(
            "model_sha256"
        ):
            raise ValueError("Model checksum mismatch")
        pipeline = joblib.load(self.model_path)
        if list(pipeline.feature_names_in_) != metadata["features"] or set(
            schema
        ) != set(metadata["features"]):
            raise ValueError("Model/schema feature mismatch")
        for bounds in schema.values():
            values = [bounds.get(key) for key in ("min", "median", "max")]
            if any(
                isinstance(v, bool)
                or not isinstance(v, (int, float))
                or not math.isfinite(v)
                for v in values
            ):
                raise ValueError("Invalid input bounds in schema")
            if not values[0] <= values[1] <= values[2]:
                raise ValueError("Invalid input bounds order")
        self.schema, self.metadata, self.pipeline = schema, metadata, pipeline

    def ensure_loaded(self) -> None:
        if self.pipeline is None:
            with self.lock:
                if self.pipeline is None:
                    self.load()

    def validate_domain(self, values):
        errors = []
        for feature, bounds in self.schema.items():
            if not bounds["min"] <= values[feature] <= bounds["max"]:
                errors.append(
                    {
                        "field": feature,
                        "message": f"Phải nằm trong khoảng train [{bounds['min']:.6g}, {bounds['max']:.6g}].",
                    }
                )
        if not float(values["Population"]).is_integer():
            errors.append(
                {"field": "Population", "message": "Dân số phải là số nguyên."}
            )
        if values["AveBedrms"] > values["AveRooms"]:
            errors.append(
                {
                    "field": "AveBedrms",
                    "message": "Số phòng ngủ không thể lớn hơn tổng số phòng.",
                }
            )
        return errors

    def predict(self, values: dict[str, float]) -> float:
        self.ensure_loaded()
        frame = pd.DataFrame([values], columns=self.metadata["features"])
        prediction = float(self.pipeline.predict(frame)[0])
        if not math.isfinite(prediction):
            raise ArithmeticError("Non-finite prediction")
        return prediction


model_service = ModelService()
