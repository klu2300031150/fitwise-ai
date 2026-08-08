from __future__ import annotations

from typing import Any

SIZE_OFFSETS = {
    "S": -4.0,
    "M": 0.0,
    "L": 4.0,
    "XL": 8.0,
}


def _apply_fabric_adjustment(base: dict[str, float], fabric: dict[str, Any]) -> tuple[dict[str, float], list[str]]:
    adjusted = dict(base)
    notes: list[str] = []
    fabric_type = (fabric.get("fabric_type") or "").lower()
    stretch_percentage = float(fabric.get("stretch_percentage") or 0)

    if "cotton" in fabric_type:
        adjusted["length"] += 1.0
        notes.append("Cotton adds a small shrink allowance to the length.")
    if "elastane" in fabric_type or stretch_percentage >= 5:
        adjusted["chest"] -= 1.0
        adjusted["waist"] -= 1.0
        notes.append(f"Fabric has {stretch_percentage:.0f}% stretch, so the fit is slightly more forgiving.")
    if "denim" in fabric_type:
        adjusted["waist"] += 1.5
        adjusted["hip"] += 1.5
        notes.append("Denim keeps a firmer waist and hip fit.")
    if fabric.get("gsm") and int(fabric["gsm"]) >= 240:
        adjusted["shoulder"] += 0.5
        notes.append("Heavier GSM adds a touch of structure.")
    return adjusted, notes


def generate_size_chart(base_measurements: dict[str, float], fabric: dict[str, Any], category: str) -> dict[str, Any]:
    baseline, fabric_notes = _apply_fabric_adjustment(base_measurements, fabric)
    sizes = []
    explainability = {"category": category, "baseline": baseline, "fabric_notes": fabric_notes}
    for size_name, offset in SIZE_OFFSETS.items():
        sizes.append(
            {
                "size": size_name,
                "chest": round(baseline["chest"] + offset, 1),
                "waist": round(baseline["waist"] + offset, 1),
                "hip": round(baseline["hip"] + offset, 1),
                "sleeve": round(baseline["sleeve"] + offset * 0.35, 1),
                "length": round(baseline["length"] + offset * 0.25, 1),
                "shoulder": round(baseline["shoulder"] + offset * 0.2, 1),
                "confidence": 0.96 if size_name == "M" else 0.9,
                "notes": [f"{size_name} generated from the M baseline."],
            }
        )
    return {"sizes": sizes, "explainability": explainability}


def recommend_size(
    customer_measurements: dict[str, float],
    size_table: list[dict[str, Any]],
    fabric: dict[str, Any] | None = None,
    historical_feedback_count: int = 0,
) -> dict[str, Any]:
    if not size_table:
        raise ValueError("Size chart is empty")

    fabric = fabric or {}
    chest = float(customer_measurements.get("chest") or 0.0)
    waist = float(customer_measurements.get("waist") or chest)
    hip = float(customer_measurements.get("hip") or waist)
    stretch_percentage = float(fabric.get("stretch_percentage") or 0.0)

    chosen_row = min(
        size_table,
        key=lambda row: abs(chest - float(row["chest"])) + abs(waist - float(row["waist"])) * 0.6 + abs(hip - float(row["hip"])) * 0.4,
    )
    best_size = chosen_row["size"]
    chest_gap = abs(chest - float(chosen_row["chest"]))

    reasons = [
        "Chest matches the closest size in the chart." if chest_gap <= 2 else f"Chest is closest to {best_size}.",
        f"Fabric has {stretch_percentage:.0f}% stretch.",
        "Comfortable fit.",
    ]
    if historical_feedback_count:
        reasons.append(f"{historical_feedback_count} similar buyer feedback samples support the choice.")

    confidence = max(0.72, min(0.99, 0.9 + stretch_percentage * 0.0075 - chest_gap * 0.01))
    return {
        "recommended_size": best_size,
        "confidence_score": round(confidence, 2),
        "explanation": reasons,
        "size_row": chosen_row,
    }
