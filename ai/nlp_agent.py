from __future__ import annotations

import re
from typing import Any

MEASUREMENT_KEYS = ("chest", "waist", "hip", "sleeve", "shoulder", "neck", "length")


def _extract_measurement(text: str, label: str) -> float | None:
    patterns = [
        rf"{label}\s*[:=]?\s*(\d+(?:\.\d+)?)",
        rf"{label}\s*(?:width|circumference|measurement)?\s*[:=]?\s*(\d+(?:\.\d+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def parse_tech_pack(text: str) -> dict[str, Any]:
    normalized = text or ""
    measurements = {key: _extract_measurement(normalized, key) for key in MEASUREMENT_KEYS}

    fabric_type_match = re.search(r"fabric\s*type\s*[:=]?\s*([A-Za-z0-9\-\s]+)", normalized, flags=re.IGNORECASE)
    weave_match = re.search(r"weave\s*type\s*[:=]?\s*([A-Za-z0-9\-\s]+)", normalized, flags=re.IGNORECASE)
    gsm_match = re.search(r"gsm\s*[:=]?\s*(\d+)", normalized, flags=re.IGNORECASE)
    stretch_match = re.search(r"stretch\s*[:=]?\s*(\d+(?:\.\d+)?)%?", normalized, flags=re.IGNORECASE)

    size_table = []
    size_table_pattern = re.compile(r"(xs|s|m|l|xl|xxl)\s*[:\-]?\s*chest\s*(\d+(?:\.\d+)?)\s*waist\s*(\d+(?:\.\d+)?)", flags=re.IGNORECASE)
    for match in size_table_pattern.finditer(normalized):
        size_table.append({"size": match.group(1).upper(), "chest": float(match.group(2)), "waist": float(match.group(3))})

    return {
        "measurements": {key: value for key, value in measurements.items() if value is not None},
        "fabric": {
            "fabric_type": fabric_type_match.group(1).strip() if fabric_type_match else None,
            "weave_type": weave_match.group(1).strip() if weave_match else None,
            "gsm": int(gsm_match.group(1)) if gsm_match else None,
            "stretch_percentage": float(stretch_match.group(1)) if stretch_match else None,
        },
        "size_table": size_table,
        "raw_text_excerpt": normalized[:750],
    }
