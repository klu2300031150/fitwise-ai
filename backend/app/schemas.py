from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")


class BodyMeasurements(APIModel):
    height: float | None = None
    weight: float | None = None
    chest: float
    waist: float
    hip: float


class RecommendationRequest(APIModel):
    product_id: str
    height: float | None = None
    weight: float | None = None
    chest: float
    waist: float
    hip: float


class SizeCell(APIModel):
    size: str
    chest: float
    waist: float
    hip: float
    sleeve: float
    length: float
    shoulder: float
    confidence: float
    notes: list[str] = []


class SizeChart(APIModel):
    id: str
    product_id: str
    sizes: list[SizeCell]
    notes: list[str]
    validation: dict[str, Any]
    created_at: datetime


class ProductRead(APIModel):
    id: str
    name: str
    category: str
    fabric_type: str
    gsm: int | None = None
    stretch_percentage: float | None = None
    weave_type: str | None = None
    front_image_path: str | None = None
    back_image_path: str | None = None
    flat_lay_image_path: str | None = None
    tech_pack_path: str | None = None
    tech_pack_text: str | None = None
    chart: SizeChart
    explanation: list[str]
    created_at: datetime


class ProductCreateResponse(APIModel):
    message: str
    product: ProductRead
    chart: SizeChart
    explanation: list[str]


class RecommendationResponse(APIModel):
    product_id: str
    recommended_size: str
    confidence_score: float
    reason: list[str]
    size_table: list[SizeCell] = []
