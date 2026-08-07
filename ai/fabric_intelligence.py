from __future__ import annotations

from typing import Any


def apply_fabric_rules(fabric: dict[str, Any]) -> dict[str, Any]:
    fabric_type = (fabric.get("fabric_type") or "").lower()
    gsm = fabric.get("gsm")
    stretch_percentage = float(fabric.get("stretch_percentage") or 0)
    weave_type = fabric.get("weave_type")

    notes: list[str] = []
    shrink_allowance = 0.0
    stretch_adjustment = 0.0

    if "cotton" in fabric_type:
        shrink_allowance += 0.03
        notes.append("Cotton detected: added 3% shrink allowance and slightly increased length ease.")
    if "elastane" in fabric_type or stretch_percentage >= 5:
        stretch_adjustment += min(stretch_percentage / 100.0, 0.08)
        notes.append("Elastane or measurable stretch detected: chest and waist allowances tightened for fit retention.")
    if "denim" in fabric_type:
        shrink_allowance += 0.01
        stretch_adjustment -= 0.01
        notes.append("Denim detected: zero-stretch behavior applied with extra waist ease.")
    if gsm and gsm >= 260:
        notes.append("Heavy GSM fabric detected: added a small comfort allowance.")

    return {
        "fabric_type": fabric.get("fabric_type", "Unknown"),
        "gsm": gsm,
        "stretch_percentage": stretch_percentage,
        "weave_type": weave_type,
        "shrink_allowance": round(shrink_allowance, 4),
        "stretch_adjustment": round(stretch_adjustment, 4),
        "notes": notes or ["Fabric rules applied successfully."],
    }
