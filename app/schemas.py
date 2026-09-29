"""Kiểu JSON nghiêm ngặt, đủ tám số hữu hạn."""

import math
from pydantic import BaseModel, ConfigDict, field_validator


class EstimateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

    @field_validator("*", mode="before")
    @classmethod
    def finite_number(cls, value):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ValueError(
                "Phải là số JSON hữu hạn; không nhận chuỗi, boolean, NaN hoặc vô hạn."
            )
        return value


class EstimateResponse(BaseModel):
    prediction: float
    unit: str
    estimated_usd: float
    model: str
    warning: str
