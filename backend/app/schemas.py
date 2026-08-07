from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")


class Token(APIModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(APIModel):
    email: EmailStr
    full_name: str
    password: str = Field(min_length=8)
    role: Literal["seller", "customer", "admin"] = "customer"


class UserRead(APIModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime


class LoginRequest(APIModel):
    email: EmailStr
    password: str


class FabricDetails(APIModel):
    fabric_type: str
    gsm: int | None = None
    stretch_percentage: float | None = None
    weave_type: str | None = None


class BodyMeasurements(APIModel):
    height: float | None = None
    weight: float | None = None
    chest: float
    waist: float
    hip: float


class BrandSelection(APIModel):
    brand_name: str
    current_size: str


class CustomerFitInput(APIModel):
    product_id: str
    measurements: BodyMeasurements | None = None
    brand: BrandSelection | None = None
    historical_feedback_count: int | None = None


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
    seller_id: str
    name: str
    category: str
    front_image_path: str | None = None
    back_image_path: str | None = None
    flat_lay_image_path: str | None = None
    tech_pack_path: str | None = None
    status: str
    extracted_text: str | None = None
    validation_summary: dict[str, Any] | None = None
    chart_summary: dict[str, Any] | None = None
    created_at: datetime


class ProductUploadResponse(APIModel):
    product: ProductRead
    fabric: FabricDetails
    measurements: dict[str, Any]
    chart: SizeChart
    explainability: dict[str, Any]


class RecommendationResponse(APIModel):
    recommendation_id: str
    product_id: str
    recommended_size: str
    confidence_score: float
    explanation: list[str]
    cache_hit: bool = False
    size_table: list[SizeCell] = []


class FeedbackCreate(APIModel):
    recommendation_id: str
    actual_size: str | None = None
    fit_rating: int | None = Field(default=None, ge=1, le=5)
    comments: str | None = None


class FeedbackRead(APIModel):
    id: str
    recommendation_id: str
    actual_size: str | None = None
    fit_rating: int | None = None
    comments: str | None = None
    created_at: datetime


class ChartRequest(APIModel):
    product_id: str


class ChartResponse(APIModel):
    chart: SizeChart


class AdminSummary(APIModel):
    total_products: int
    total_recommendations: int
    cache_hit_rate: float
    validation_alerts: list[str]
    top_sizing_trends: list[dict[str, Any]]


class UploadSummary(APIModel):
    uploaded_files: list[str]
    validation_alerts: list[str]
