from __future__ import annotations

import re
import sys
from pathlib import Path

import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / "pdf_validation.md"

EXPECTED = {
    "同济高数第七版_第一章_习题册_中文.pdf": (264, 198, "同济高数第一章·习题册"),
    "同济高数第七版_第一章_超详细解析_中文.pdf": (198, 264, "同济高数第一章·超详细解析"),
    "Tongji_Calculus_7e_Chapter_1_Exercises_EN.pdf": (
        264,
        198,
        "Tongji Calculus Chapter 1 · Exercises",
    ),
    "Tongji_Calculus_7e_Chapter_1_Detailed_Solutions_EN.pdf": (
        198,
        264,
        "Tongji Calculus Chapter 1 · Detailed Solutions",
    ),
}


def _points_to_mm(value: float) -> float:
    return value * 25.4 / 72


def _is_content_blank(text: str, running_title: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    remaining = [
        line
        for line in lines
        if line != running_title and not re.fullmatch(r"\d+", line)
    ]
    return not remaining


def main() -> int:
    errors: list[str] = []
    report_lines = ["# PDF validation", ""]
    for name, (width_mm, height_mm, running_title) in EXPECTED.items():
        path = DIST / name
        if not path.exists():
            errors.append(f"Missing {name}")
            continue
        reader = PdfReader(path)
        first = reader.pages[0]
        actual_width = _points_to_mm(float(first.mediabox.width))
        actual_height = _points_to_mm(float(first.mediabox.height))
        if abs(actual_width - width_mm) > 0.5 or abs(actual_height - height_mm) > 0.5:
            errors.append(
                f"{name}: expected {width_mm}x{height_mm} mm, got {actual_width:.1f}x{actual_height:.1f} mm"
            )

        with pdfplumber.open(path) as pdf:
            texts = [(page.extract_text() or "").strip() for page in pdf.pages]
        combined = "\n".join(texts)
        ids = set(re.findall(r"\bQ\d{3}\b", combined))
        missing_ids = [f"Q{index:03d}" for index in range(1, 101) if f"Q{index:03d}" not in ids]
        markup_residuals = sorted(
            token
            for token in ("\\", "$", "widetilde", "mathbb", "�", "□")
            if token in combined
        )
        blank_pages = [
            index
            for index, text in enumerate(texts, start=1)
            if _is_content_blank(text, running_title)
        ]
        if missing_ids:
            errors.append(f"{name}: missing question IDs {missing_ids}")
        if markup_residuals:
            errors.append(f"{name}: unresolved markup or missing-glyph tokens {markup_residuals}")
        if blank_pages:
            errors.append(f"{name}: content-blank pages {blank_pages}")
        report_lines.extend(
            [
                f"## {name}",
                "",
                f"- Pages: {len(reader.pages)}",
                f"- Page size: {actual_width:.1f} × {actual_height:.1f} mm",
                f"- File size: {path.stat().st_size:,} bytes",
                f"- Question IDs found: {len(ids)}",
                f"- Content-blank pages: {blank_pages or 'None'}",
                f"- Unresolved markup/missing-glyph tokens: {markup_residuals or 'None'}",
                "",
            ]
        )

    report_lines.extend(["## Errors", ""])
    report_lines.extend([f"- {error}" for error in errors] or ["- None"])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("PDF validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
