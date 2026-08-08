from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    fabric_type: Mapped[str] = mapped_column(String(120), nullable=False)
    gsm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stretch_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    weave_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    front_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    back_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    flat_lay_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tech_pack_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tech_pack_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    chart_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    explanation_json: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    recommendations = relationship("Recommendation", back_populates="product")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    height: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    chest: Mapped[float] = mapped_column(Float, nullable=False)
    waist: Mapped[float] = mapped_column(Float, nullable=False)
    hip: Mapped[float] = mapped_column(Float, nullable=False)
    recommended_size: Mapped[str] = mapped_column(String(16), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    reason_json: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="recommendations")

