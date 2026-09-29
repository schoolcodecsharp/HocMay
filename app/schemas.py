"""Schema và kiểm tra input cho API ước lượng."""

from __future__ import annotations

import math
import json

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.model_service import SCHEMA_PATH


class EstimateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

    @field_validator("*")
    @classmethod
    def finite_number(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("Giá trị phải là số hữu hạn, không được NaN hoặc vô hạn.")
        return value

    @model_validator(mode="after")
    def inside_observed_domain(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        errors = []
        for feature, bounds in schema.items():
            value = getattr(self, feature)
            if value < bounds["min"] or value > bounds["max"]:
                errors.append(
                    f"{feature} phải nằm trong khoảng dữ liệu train "
                    f"[{bounds['min']:.4g}, {bounds['max']:.4g}]."
                )
        if errors:
            raise ValueError(" ".join(errors))
        return self


class EstimateResponse(BaseModel):
    prediction: float
    unit: str
    estimated_usd: float
    model: str
    warning: str
