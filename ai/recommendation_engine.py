from __future__ import annotations

from typing import Any

SIZE_GRADES = {
    "XS": -0.08,
    "S": -0.04,
    "M": 0.0,
    "L": 0.04,
    "XL": 0.08,
    "XXL": 0.12,
}

MEASUREMENT_KEYS = ("chest", "waist", "hip", "sleeve", "length", "shoulder")


def _apply_fabric_ease(base: dict[str, float], fabric: dict[str, Any]) -> tuple[dict[str, float], list[str]]:
    adjusted = dict(base)
    notes: list[str] = []
    fabric_type = (fabric.get("fabric_type") or "").lower()
    stretch_percentage = float(fabric.get("stretch_percentage") or 0)
    shrink_allowance = float(fabric.get("shrink_allowance") or 0)
    stretch_adjustment = float(fabric.get("stretch_adjustment") or 0)

    if "cotton" in fabric_type:
        adjusted["length"] = adjusted["length"] * (1 + shrink_allowance)
        adjusted["waist"] += 1.0
        notes.append("Cotton shrink allowance increased length and waist ease.")
    if "elastane" in fabric_type or stretch_percentage >= 5:
        factor = max(0.0, 1 - stretch_adjustment - 0.01)
        adjusted["chest"] *= factor
        adjusted["waist"] *= factor
        notes.append(f"Stretch content of {stretch_percentage:.1f}% tightened the chest and waist fit.")
    if "denim" in fabric_type:
        adjusted["waist"] += 1.5
        adjusted["hip"] += 1.5
        notes.append("Denim rigidity added extra waist and hip allowance.")
    if fabric.get("gsm") and fabric["gsm"] >= 260:
        adjusted["length"] += 0.5
        notes.append("Heavy GSM added a small comfort allowance.")
    return adjusted, notes


def generate_size_chart(base_measurements: dict[str, float], fabric: dict[str, Any], category: str) -> dict[str, Any]:
    baseline, fabric_notes = _apply_fabric_ease(base_measurements, fabric)
    sizes = []
    explainability = {
        "category": category,
        "baseline": baseline,
        "fabric_notes": fabric_notes,
    }
    for size_name, grade in SIZE_GRADES.items():
        notes = [f"{size_name} generated using a {grade:+.0%} grade from the M baseline."]
        if size_name == "M":
            notes.append("M is aligned to the extracted garment baseline.")
        sizes.append(
            {
                "size": size_name,
                "chest": round(baseline["chest"] * (1 + grade), 1),
                "waist": round(baseline["waist"] * (1 + grade), 1),
                "hip": round(baseline["hip"] * (1 + grade), 1),
                "sleeve": round(baseline["sleeve"] * (1 + grade * 0.45), 1),
                "length": round(baseline["length"] * (1 + grade * 0.35), 1),
                "shoulder": round(baseline["shoulder"] * (1 + grade * 0.3), 1),
                "confidence": round(max(0.72, 0.96 - abs(grade) * 0.65), 2),
                "notes": notes,
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
    target = {
        "chest": float(customer_measurements.get("chest") or 0.0),
        "waist": float(customer_measurements.get("waist") or 0.0),
        "hip": float(customer_measurements.get("hip") or 0.0),
    }

    best_size = None
    best_score = float("inf")
    best_row = None
    reasons: list[str] = []

    for row in size_table:
        error = 0.0
        error += abs(target["chest"] - float(row["chest"])) / max(float(row["chest"]), 1.0)
        error += abs(target["waist"] - float(row["waist"])) / max(float(row["waist"]), 1.0)
        error += abs(target["hip"] - float(row["hip"])) / max(float(row["hip"]), 1.0)
        if error < best_score:
            best_score = error
            best_size = row["size"]
            best_row = row

    if best_row is None:
        raise ValueError("Unable to determine a recommendation")

    explanation = [
        f"Chest is closest to {best_size} with a normalized fit error of {best_score:.3f}.",
        f"Fabric stretch input: {float(fabric.get('stretch_percentage') or 0):.1f}%.",
    ]
    if float(fabric.get("stretch_percentage") or 0) >= 5:
        explanation.append("Stretch fabric slightly improves fit tolerance across adjacent sizes.")
    if historical_feedback_count:
        explanation.append(f"{historical_feedback_count} similar historical feedback samples informed the confidence prior.")

    confidence = max(0.55, min(0.99, 0.985 - best_score * 1.75 + min(historical_feedback_count * 0.01, 0.08)))
    if best_size:
        reasons.append(f"Selected {best_size} because it minimized combined chest, waist, and hip deviation.")
    return {
        "recommended_size": best_size,
        "confidence_score": round(confidence, 2),
        "explanation": reasons + explanation,
        "size_row": best_row,
    }
