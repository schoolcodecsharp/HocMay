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
        # JSON có thể chứa số nguyên lớn hơn miền float của Python.
        try:
            valid = (
                not isinstance(value, bool)
                and isinstance(value, (int, float))
                and math.isfinite(value)
            )
        except OverflowError:
            valid = False
        if not valid:
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
