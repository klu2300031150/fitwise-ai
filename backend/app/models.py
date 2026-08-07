from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="customer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    products = relationship("Product", back_populates="seller")
    profiles = relationship("CustomerProfile", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    seller_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    front_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    back_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    flat_lay_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tech_pack_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    validation_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    chart_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    seller = relationship("User", back_populates="products")
    fabric_spec = relationship("FabricSpec", back_populates="product", uselist=False, cascade="all, delete-orphan")
    measurements = relationship("Measurement", back_populates="product", cascade="all, delete-orphan")
    generated_chart = relationship("GeneratedSizeChart", back_populates="product", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="product")


class FabricSpec(Base):
    __tablename__ = "fabric_specs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), unique=True, nullable=False)
    fabric_type: Mapped[str] = mapped_column(String(120), nullable=False)
    gsm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stretch_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    weave_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    shrink_allowance: Mapped[float | None] = mapped_column(Float, nullable=True)
    stretch_adjustment: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="fabric_spec")


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    chest: Mapped[float] = mapped_column(Float, nullable=False)
    waist: Mapped[float] = mapped_column(Float, nullable=False)
    hip: Mapped[float] = mapped_column(Float, nullable=False)
    sleeve: Mapped[float] = mapped_column(Float, nullable=False)
    shoulder: Mapped[float] = mapped_column(Float, nullable=False)
    neck: Mapped[float] = mapped_column(Float, nullable=False)
    length: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="measurements")


class GeneratedSizeChart(Base):
    __tablename__ = "generated_size_charts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), unique=True, nullable=False)
    chart_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    explainability_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    validation_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="generated_chart")


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    height: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    chest: Mapped[float | None] = mapped_column(Float, nullable=True)
    waist: Mapped[float | None] = mapped_column(Float, nullable=True)
    hip: Mapped[float | None] = mapped_column(Float, nullable=True)
    brand_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    current_size: Mapped[str | None] = mapped_column(String(16), nullable=True)
    feature_embedding: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="profiles")
    recommendations = relationship("Recommendation", back_populates="customer_profile")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    customer_profile_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("customer_profiles.id"), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    recommended_size: Mapped[str] = mapped_column(String(16), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    explanation_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    request_snapshot_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="recommendations")
    customer_profile = relationship("CustomerProfile", back_populates="recommendations")
    user = relationship("User", back_populates="recommendations")
    feedback = relationship("Feedback", back_populates="recommendation", uselist=False, cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    recommendation_id: Mapped[str] = mapped_column(String(36), ForeignKey("recommendations.id"), unique=True, nullable=False)
    actual_size: Mapped[str | None] = mapped_column(String(16), nullable=True)
    fit_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    recommendation = relationship("Recommendation", back_populates="feedback")
