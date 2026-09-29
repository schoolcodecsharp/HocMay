"""Nạp artifact và thực hiện prediction; không huấn luyện trong web request."""

from __future__ import annotations

import json
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

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Không tìm thấy model artifact: {self.model_path}")
        self.pipeline = joblib.load(self.model_path)
        self.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    def ensure_loaded(self) -> None:
        if self.pipeline is None:
            self.load()

    def predict(self, values: dict[str, float]) -> float:
        self.ensure_loaded()
        frame = pd.DataFrame([values], columns=self.metadata["features"])
        return float(self.pipeline.predict(frame)[0])


model_service = ModelService()
