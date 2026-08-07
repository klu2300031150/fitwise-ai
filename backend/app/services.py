from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from ai.fabric_intelligence import apply_fabric_rules
from ai.nlp_agent import parse_tech_pack
from ai.ocr_agent import extract_tech_pack_text
from ai.recommendation_engine import generate_size_chart, recommend_size
from ai.vision_agent import estimate_measurements_from_images
from app.core.config import settings
from app.core.security import hash_password
from app.models import CustomerProfile, FabricSpec, Feedback, GeneratedSizeChart, Measurement, Product, Recommendation, User

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_DOC_EXTENSIONS = {".pdf", ".txt"}
BRAND_PRIORS = {
    "nike": {"chest": -0.8, "waist": -0.6, "hip": -0.5},
    "adidas": {"chest": 0.2, "waist": 0.0, "hip": 0.0},
    "puma": {"chest": -1.0, "waist": -0.7, "hip": -0.4},
}


def ensure_storage() -> Path:
    storage_root = Path(settings.storage_dir)
    storage_root.mkdir(parents=True, exist_ok=True)
    return storage_root


def save_upload_file(product_id: str, file_name: str | None, stream, subdir: str) -> str | None:
    if not file_name:
        return None
    suffix = Path(file_name).suffix.lower()
    allowed = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_DOC_EXTENSIONS
    if suffix not in allowed:
        raise ValueError(f"Unsupported upload type: {suffix}")
    target_dir = ensure_storage() / product_id / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{Path(file_name).stem.replace(' ', '_')}{suffix}"
    target_path = target_dir / safe_name
    with target_path.open("wb") as file_object:
        shutil.copyfileobj(stream, file_object)
    return str(target_path)


def _normalize_float(value: float | int | None, default: float = 0.0) -> float:
    if value is None:
        return default
    return float(value)


def build_fabric_spec(fabric_type: str, gsm: int | None, stretch_percentage: float | None, weave_type: str | None) -> dict[str, Any]:
    spec = {
        "fabric_type": fabric_type,
        "gsm": gsm,
        "stretch_percentage": stretch_percentage,
        "weave_type": weave_type,
    }
    return apply_fabric_rules(spec)


def parse_and_structure_tech_pack(tech_pack_path: str | None) -> tuple[str, dict[str, Any]]:
    if not tech_pack_path:
        return "", {"measurements": {}, "fabric": {}, "size_table": []}
    text = extract_tech_pack_text(tech_pack_path)
    parsed = parse_tech_pack(text)
    return text, parsed


def create_product_and_chart(
    db: Session,
    seller: User,
    name: str,
    category: str,
    front_image,
    back_image,
    flat_lay_image,
    tech_pack,
    fabric_type: str,
    gsm: int | None,
    stretch_percentage: float | None,
    weave_type: str | None,
) -> tuple[Product, GeneratedSizeChart, dict[str, Any]]:
    product = Product(seller_id=seller.id, name=name, category=category, status="processing")
    db.add(product)
    db.flush()

    product.front_image_path = save_upload_file(product.id, getattr(front_image, "filename", None), getattr(front_image, "file", None), "images")
    product.back_image_path = save_upload_file(product.id, getattr(back_image, "filename", None), getattr(back_image, "file", None), "images")
    product.flat_lay_image_path = save_upload_file(product.id, getattr(flat_lay_image, "filename", None), getattr(flat_lay_image, "file", None), "images")
    product.tech_pack_path = save_upload_file(product.id, getattr(tech_pack, "filename", None), getattr(tech_pack, "file", None), "tech-packs")

    fabric_payload = build_fabric_spec(fabric_type, gsm, stretch_percentage, weave_type)
    fabric = FabricSpec(
        product_id=product.id,
        fabric_type=fabric_payload["fabric_type"],
        gsm=fabric_payload.get("gsm"),
        stretch_percentage=fabric_payload.get("stretch_percentage"),
        weave_type=fabric_payload.get("weave_type"),
        shrink_allowance=fabric_payload.get("shrink_allowance"),
        stretch_adjustment=fabric_payload.get("stretch_adjustment"),
        notes=fabric_payload.get("notes"),
    )
    db.add(fabric)

    tech_pack_text, parsed = parse_and_structure_tech_pack(product.tech_pack_path)
    product.extracted_text = tech_pack_text

    vision = estimate_measurements_from_images(
        product.front_image_path,
        product.back_image_path,
        product.flat_lay_image_path,
        category=category,
    )
    measurement_payload = parsed.get("measurements") or {}
    baseline = {
        "chest": _normalize_float(measurement_payload.get("chest"), vision.chest),
        "waist": _normalize_float(measurement_payload.get("waist"), vision.waist),
        "hip": _normalize_float(measurement_payload.get("hip"), vision.hip),
        "sleeve": _normalize_float(measurement_payload.get("sleeve"), vision.sleeve),
        "shoulder": _normalize_float(measurement_payload.get("shoulder"), vision.shoulder),
        "neck": _normalize_float(measurement_payload.get("neck"), vision.neck),
        "length": _normalize_float(measurement_payload.get("length"), vision.length),
    }

    measurement = Measurement(
        product_id=product.id,
        source="vision+ocr+nlp",
        chest=baseline["chest"],
        waist=baseline["waist"],
        hip=baseline["hip"],
        sleeve=baseline["sleeve"],
        shoulder=baseline["shoulder"],
        neck=baseline["neck"],
        length=baseline["length"],
        confidence=vision.confidence,
        raw_data={"vision": vision.as_dict(), "ocr": parsed, "fabric": fabric_payload},
    )
    db.add(measurement)
    db.flush()

    chart_payload = generate_size_chart(baseline, fabric_payload, category)
    validation = validate_measurements(baseline, fabric_payload)
    generated_chart = GeneratedSizeChart(
        product_id=product.id,
        chart_json=chart_payload["sizes"],
        explainability_json=chart_payload["explainability"],
        validation_json={"alerts": validation},
    )
    product.status = "ready"
    product.validation_summary = {"alerts": validation}
    product.chart_summary = chart_payload["explainability"]
    db.add(generated_chart)
    db.commit()
    db.refresh(product)
    db.refresh(generated_chart)
    return product, generated_chart, {"vision": vision.as_dict(), "parsed": parsed, "fabric": fabric_payload, "baseline": baseline}


def regenerate_chart_for_product(db: Session, product: Product) -> GeneratedSizeChart:
    measurement = db.query(Measurement).filter(Measurement.product_id == product.id).order_by(Measurement.created_at.desc()).first()
    fabric = product.fabric_spec
    if not measurement or not fabric:
        raise ValueError("Product needs measurement and fabric information before chart generation")
    baseline = {
        "chest": measurement.chest,
        "waist": measurement.waist,
        "hip": measurement.hip,
        "sleeve": measurement.sleeve,
        "shoulder": measurement.shoulder,
        "neck": measurement.neck,
        "length": measurement.length,
    }
    fabric_payload = {
        "fabric_type": fabric.fabric_type,
        "gsm": fabric.gsm,
        "stretch_percentage": fabric.stretch_percentage,
        "weave_type": fabric.weave_type,
        "shrink_allowance": fabric.shrink_allowance,
        "stretch_adjustment": fabric.stretch_adjustment,
        "notes": fabric.notes,
    }
    chart_payload = generate_size_chart(baseline, fabric_payload, product.category)
    validation = validate_measurements(baseline, fabric_payload)
    if product.generated_chart:
        product.generated_chart.chart_json = chart_payload["sizes"]
        product.generated_chart.explainability_json = chart_payload["explainability"]
        product.generated_chart.validation_json = {"alerts": validation}
        generated = product.generated_chart
    else:
        generated = GeneratedSizeChart(
            product_id=product.id,
            chart_json=chart_payload["sizes"],
            explainability_json=chart_payload["explainability"],
            validation_json={"alerts": validation},
        )
        db.add(generated)
    product.validation_summary = {"alerts": validation}
    product.chart_summary = chart_payload["explainability"]
    db.commit()
    db.refresh(generated)
    return generated


def validate_measurements(measurements: dict[str, float], fabric: dict[str, Any]) -> list[str]:
    alerts: list[str] = []
    ranges = {
        "chest": (60.0, 160.0),
        "waist": (50.0, 150.0),
        "hip": (70.0, 170.0),
        "sleeve": (40.0, 100.0),
        "shoulder": (35.0, 75.0),
        "neck": (30.0, 55.0),
        "length": (45.0, 120.0),
    }
    for key, value in measurements.items():
        low, high = ranges[key]
        if value <= 0:
            alerts.append(f"{key.title()} is missing or non-positive.")
        elif value < low or value > high:
            alerts.append(f"{key.title()} looks like an outlier ({value:.1f} cm).")
    stretch = fabric.get("stretch_percentage") or 0
    gsm = fabric.get("gsm") or 0
    if stretch < 0 or stretch > 40:
        alerts.append("Stretch percentage is outside the normal apparel range.")
    if gsm and gsm > 500:
        alerts.append("GSM is unusually high for a retail apparel SKU.")
    if not alerts:
        alerts.append("Measurements validated successfully.")
    return alerts


def recommendation_cache_key(product_id: str, payload: dict[str, Any]) -> str:
    canonical = json.dumps({"product_id": product_id, **payload}, sort_keys=True, default=str)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"fitwise:recommendation:{digest}"


def current_size_order(size: str) -> int:
    normalized = size.upper().strip()
    if normalized not in SIZE_ORDER:
        return 2
    return SIZE_ORDER.index(normalized)


def brand_adjustments(brand_name: str | None) -> dict[str, float]:
    if not brand_name:
        return {"chest": 0.0, "waist": 0.0, "hip": 0.0}
    return BRAND_PRIORS.get(brand_name.lower(), {"chest": 0.0, "waist": 0.0, "hip": 0.0})


def similar_feedback_boost(db: Session, product_id: str, recommended_size: str) -> float:
    query = (
        db.query(func.avg(Feedback.fit_rating))
        .join(Recommendation, Recommendation.id == Feedback.recommendation_id)
        .filter(Recommendation.product_id == product_id)
        .filter(Recommendation.recommended_size == recommended_size)
    )
    average = query.scalar() or 0.0
    return min(float(average) * 0.015, 0.06)


def upsert_customer_profile(db: Session, request_payload: dict[str, Any]) -> CustomerProfile:
    measurements = request_payload.get("measurements") or {}
    brand = request_payload.get("brand") or {}
    profile = CustomerProfile(
        height=measurements.get("height"),
        weight=measurements.get("weight"),
        chest=measurements.get("chest"),
        waist=measurements.get("waist"),
        hip=measurements.get("hip"),
        brand_name=brand.get("brand_name"),
        current_size=brand.get("current_size"),
        feature_embedding={
            "measurement_hash": hashlib.sha256(json.dumps(request_payload, sort_keys=True, default=str).encode("utf-8")).hexdigest(),
        },
    )
    db.add(profile)
    db.flush()
    return profile


def generate_recommendation(db: Session, product: Product, payload: dict[str, Any]) -> tuple[str, float, list[str], list[dict[str, Any]]]:
    chart = product.generated_chart
    if not chart:
        raise ValueError("Generate the size chart first")
    chart_rows = chart.chart_json
    target = payload.get("measurements") or {}
    brand = payload.get("brand") or {}
    if brand.get("brand_name"):
        adjustments = brand_adjustments(brand.get("brand_name"))
        target = {
            "chest": _normalize_float(target.get("chest"), 0.0) + adjustments["chest"],
            "waist": _normalize_float(target.get("waist"), 0.0) + adjustments["waist"],
            "hip": _normalize_float(target.get("hip"), 0.0) + adjustments["hip"],
        }
    result = recommend_size(target, chart_rows, product.fabric_spec, payload.get("historical_feedback_count") or 0)
    feedback_boost = similar_feedback_boost(db, product.id, result["recommended_size"])
    confidence = min(result["confidence_score"] + feedback_boost, 0.99)
    explanation = result["explanation"][:]
    if feedback_boost > 0:
        explanation.append("Historical feedback increased confidence for this size.")
    return result["recommended_size"], confidence, explanation, chart_rows


def admin_summary(db: Session) -> dict[str, Any]:
    total_products = db.query(func.count(Product.id)).scalar() or 0
    total_recommendations = db.query(func.count(Recommendation.id)).scalar() or 0
    cached_rows = db.query(Recommendation).all()
    total_cached = sum(1 for row in cached_rows if bool((row.request_snapshot_json or {}).get("cache_hit")))
    cache_hit_rate = round((total_cached / total_recommendations) if total_recommendations else 0.0, 3)
    validation_alerts = []
    products = db.query(Product).order_by(Product.created_at.desc()).limit(5).all()
    for product in products:
        alerts = (product.validation_summary or {}).get("alerts", [])
        validation_alerts.extend([f"{product.name}: {alert}" for alert in alerts if "validated successfully" not in alert.lower()])
    top_trends = []
    for row in db.query(Recommendation.recommended_size, func.count(Recommendation.id)).group_by(Recommendation.recommended_size).order_by(func.count(Recommendation.id).desc()).all():
        top_trends.append({"size": row[0], "count": row[1]})
    return {
        "total_products": total_products,
        "total_recommendations": total_recommendations,
        "cache_hit_rate": cache_hit_rate,
        "validation_alerts": validation_alerts[:6],
        "top_sizing_trends": top_trends,
    }
