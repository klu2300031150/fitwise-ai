from __future__ import annotations

import json
import re
import shutil
import uuid
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from ai.fabric_intelligence import apply_fabric_rules
from ai.nlp_agent import parse_tech_pack
from ai.ocr_agent import extract_tech_pack_text
from ai.recommendation_engine import generate_size_chart, recommend_size
from ai.vision_agent import estimate_measurements_from_images
from app.core.config import settings
from app.models import Product, Recommendation
from pypdf import PdfReader

DEFAULT_BASELINE = {
    "chest": 96.0,
    "waist": 82.0,
    "hip": 98.0,
    "sleeve": 59.0,
    "length": 70.0,
    "shoulder": 45.0,
}

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_DOC_EXTENSIONS = {".pdf", ".txt"}


def ensure_storage() -> Path:
    storage_root = Path(settings.storage_dir)
    storage_root.mkdir(parents=True, exist_ok=True)
    return storage_root


def save_upload_file(product_id: str, file_name: str | None, stream, subdir: str) -> str | None:
    if not file_name or stream is None:
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


def extract_tech_pack_text(file_path: str | None) -> str:
    if not file_path:
        return ""
    path = Path(file_path)
    if not path.exists():
        return ""
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() != ".pdf":
        return ""
    try:
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    except Exception:
        return ""


def parse_measurements_from_text(text: str) -> dict[str, float]:
    measurements: dict[str, float] = {}
    for key in ("chest", "waist", "hip", "sleeve", "shoulder", "length"):
        match = re.search(rf"{key}\s*[:=]?\s*(\d+(?:\.\d+)?)", text, flags=re.IGNORECASE)
        if match:
            measurements[key] = float(match.group(1))
    return measurements


def default_baseline_from_product(fabric_type: str, gsm: int | None, stretch_percentage: float | None) -> dict[str, float]:
    baseline = dict(DEFAULT_BASELINE)
    fabric = fabric_type.lower()
    stretch = float(stretch_percentage or 0)
    if "cotton" in fabric:
        baseline["length"] += 1.0
    if "elastane" in fabric or stretch >= 5:
        baseline["chest"] -= 0.5
        baseline["waist"] -= 0.5
    if gsm and gsm >= 240:
        baseline["shoulder"] += 0.5
    return baseline


def build_chart_payload(
    category: str,
    fabric_type: str,
    gsm: int | None,
    stretch_percentage: float | None,
    weave_type: str | None,
    tech_pack_text: str,
    front_image_path: str | None,
    back_image_path: str | None,
    flat_lay_image_path: str | None,
) -> tuple[dict[str, float], dict[str, Any], list[str]]:
    fabric_info = parse_tech_pack(tech_pack_text)
    fabric_rules = apply_fabric_rules({
        "fabric_type": fabric_info["fabric"].get("fabric_type") or fabric_type,
        "gsm": fabric_info["fabric"].get("gsm") or gsm,
        "stretch_percentage": fabric_info["fabric"].get("stretch_percentage") or stretch_percentage,
        "weave_type": fabric_info["fabric"].get("weave_type") or weave_type,
    })

    baseline = default_baseline_from_product(
        fabric_rules["fabric_type"], fabric_rules["gsm"], fabric_rules["stretch_percentage"]
    )
    parsed = parse_measurements_from_text(tech_pack_text)
    if parsed:
        baseline.update(parsed)

    vision_estimate = estimate_measurements_from_images(
        front_image_path, back_image_path, flat_lay_image_path, category
    )
    if vision_estimate.confidence >= 0.7:
        baseline = {
            "chest": round((baseline["chest"] + vision_estimate.chest) / 2.0, 1),
            "waist": round((baseline["waist"] + vision_estimate.waist) / 2.0, 1),
            "hip": round((baseline["hip"] + vision_estimate.hip) / 2.0, 1),
            "sleeve": round((baseline["sleeve"] + vision_estimate.sleeve) / 2.0, 1),
            "length": round((baseline["length"] + vision_estimate.length) / 2.0, 1),
            "shoulder": round((baseline["shoulder"] + vision_estimate.shoulder) / 2.0, 1),
        }

    fabric_payload = {
        "fabric_type": fabric_rules["fabric_type"],
        "gsm": fabric_rules["gsm"],
        "stretch_percentage": fabric_rules["stretch_percentage"],
        "weave_type": fabric_rules["weave_type"],
    }
    chart_payload = generate_size_chart(baseline, fabric_payload, category)
    explanation = [
        "Product saved successfully.",
        *fabric_rules.get("notes", []),
        *chart_payload["explainability"].get("fabric_notes", []),
        f"Tech pack text was parsed from {len(tech_pack_text)} characters.",
        f"Vision analysis confidence: {vision_estimate.confidence:.2f}.",
    ]
    return baseline, chart_payload, explanation


def create_product_record(
    db: Session,
    *,
    name: str,
    category: str,
    fabric_type: str,
    gsm: int | None,
    stretch_percentage: float | None,
    weave_type: str | None,
    front_image,
    back_image,
    flat_lay_image,
    tech_pack,
) -> Product:
    product_id = str(uuid.uuid4())
    front_image_path = save_upload_file(product_id, getattr(front_image, "filename", None), getattr(front_image, "file", None), "images")
    back_image_path = save_upload_file(product_id, getattr(back_image, "filename", None), getattr(back_image, "file", None), "images")
    flat_lay_image_path = save_upload_file(product_id, getattr(flat_lay_image, "filename", None), getattr(flat_lay_image, "file", None), "images")
    tech_pack_path = save_upload_file(product_id, getattr(tech_pack, "filename", None), getattr(tech_pack, "file", None), "tech-packs")

    product = Product(
        id=product_id,
        name=name,
        category=category,
        fabric_type=fabric_type,
        gsm=gsm,
        stretch_percentage=stretch_percentage,
        weave_type=weave_type,
        front_image_path=front_image_path,
        back_image_path=back_image_path,
        flat_lay_image_path=flat_lay_image_path,
        tech_pack_path=tech_pack_path,
        tech_pack_text=extract_tech_pack_text(tech_pack_path),
        chart_json=[],
        explanation_json=[],
    )

    tech_pack_text = product.tech_pack_text or ""
    _, chart_payload, explanation = build_chart_payload(
        category,
        fabric_type,
        gsm,
        stretch_percentage,
        weave_type,
        tech_pack_text,
        front_image_path,
        back_image_path,
        flat_lay_image_path,
    )
    product.chart_json = chart_payload["sizes"]
    product.explanation_json = explanation
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def recommend_for_product(product: Product, measurements: dict[str, float]) -> dict[str, Any]:
    result = recommend_size(measurements, product.chart_json, {
        "fabric_type": product.fabric_type,
        "gsm": product.gsm,
        "stretch_percentage": product.stretch_percentage,
        "weave_type": product.weave_type,
    })
    return result


def seed_demo_product(db: Session) -> Product | None:
    products = db.query(Product).filter(Product.name == "Aero Performance Tee").all()
    if products:
        primary = products[0]
        for duplicate in products[1:]:
            db.delete(duplicate)
        db.commit()
        return primary

    _, chart_payload, explanation = build_chart_payload(
        "Tops",
        "95% Cotton / 5% Elastane",
        180,
        8.0,
        "Jersey Knit",
        "Chest: 96\nWaist: 82\nHip: 98\nSleeve: 59\nShoulder: 45\nLength: 70",
        None,
        None,
        None,
    )
    product = Product(
        name="Aero Performance Tee",
        category="Tops",
        fabric_type="95% Cotton / 5% Elastane",
        gsm=180,
        stretch_percentage=8.0,
        weave_type="Jersey Knit",
        tech_pack_text="Chest: 96 Waist: 82 Hip: 98",
        chart_json=chart_payload["sizes"],
        explanation_json=explanation,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    recommendation = Recommendation(
        product_id=product.id,
        height=175,
        weight=72,
        chest=96,
        waist=82,
        hip=98,
        recommended_size="M",
        confidence_score=0.96,
        reason_json=["Chest matches.", "Fabric has 8% stretch.", "Comfortable fit."],
    )
    db.add(recommendation)
    db.commit()
    return product
