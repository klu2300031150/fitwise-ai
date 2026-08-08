from __future__ import annotations

from pathlib import Path

import pdfplumber
from pypdf import PdfReader


def extract_tech_pack_text(pdf_path: str | None) -> str:
    if not pdf_path:
        return ""
    path = Path(pdf_path)
    if not path.exists():
        return ""
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() != ".pdf":
        return path.read_text(encoding="utf-8", errors="ignore")

    try:
        with pdfplumber.open(str(path)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages).strip()
    except Exception:
        reader = PdfReader(str(path))
        pages = []
        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception:
                pages.append("")
        return "\n".join(pages).strip()
