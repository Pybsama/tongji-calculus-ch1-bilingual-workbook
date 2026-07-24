from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.bilingual_checks import bilingual_warnings, validate_bilingual
from src.corpus import load_questions, validate_questions


BANNED = re.compile(
    r"洛必达|l['’]?h[oô]pital|泰勒|taylor|求导|derivative|differentiat|幂级数|power series",
    re.IGNORECASE,
)


def main() -> int:
    questions = load_questions(ROOT / "content" / "questions.json")
    structural = validate_questions(questions, enforce_quotas=True)
    bilingual = validate_bilingual(questions)
    editorial: list[str] = []

    for item in questions:
        for language in ("zh", "en"):
            localized = item[language]
            solution = localized["solution"]
            searchable = " ".join(solution["steps"])
            if BANNED.search(searchable):
                editorial.append(f"{item['id']} ({language}) uses a forbidden later-chapter method")
            if len(solution["steps"]) < 4:
                editorial.append(f"{item['id']} ({language}) has fewer than four detailed steps")
            if len(solution["analysis"]) < 24:
                editorial.append(f"{item['id']} ({language}) analysis is too short")
            if len(solution["verification"]) < 12:
                editorial.append(f"{item['id']} ({language}) verification is too short")

    uniform_items = [
        item
        for item in questions
        if any(
            "一致连续" in tag or "uniform continuity" in tag.lower()
            for tag in item["tags"]["zh"] + item["tags"]["en"]
        )
    ]
    if len(uniform_items) != 2:
        editorial.append(f"Expected exactly two uniform-continuity items, got {len(uniform_items)}")

    content_report = ROOT / "reports" / "content_validation.md"
    content_report.parent.mkdir(parents=True, exist_ok=True)
    distributions = {
        "sections": Counter(item["section"] for item in questions),
        "types": Counter(item["type"] for item in questions),
        "difficulty": Counter(item["difficulty"] for item in questions),
        "classic_method": Counter(item["classic_method"] for item in questions),
    }
    all_content_errors = structural + editorial
    content_lines = [
        "# Content validation",
        "",
        f"- Questions: {len(questions)}",
        f"- Structural errors: {len(structural)}",
        f"- Editorial errors: {len(editorial)}",
        f"- Textbook-method adaptations: {distributions['classic_method'][True]}",
        f"- Uniform-continuity optional items: {len(uniform_items)}",
        "",
        "## Distributions",
        "",
        f"- Sections: `{dict(sorted(distributions['sections'].items()))}`",
        f"- Types: `{dict(sorted(distributions['types'].items()))}`",
        f"- Difficulty: `{dict(sorted(distributions['difficulty'].items()))}`",
        "",
        "## Errors",
        "",
    ]
    content_lines.extend([f"- {error}" for error in all_content_errors] or ["- None"])
    content_report.write_text("\n".join(content_lines) + "\n", encoding="utf-8")

    bilingual_report = ROOT / "reports" / "bilingual_validation.md"
    parity_warnings = [
        f"{item['id']}: {warning}"
        for item in questions
        for warning in bilingual_warnings(item)
    ]
    bilingual_lines = [
        "# Bilingual validation",
        "",
        f"- Questions checked: {len(questions)}",
        f"- Hard parity errors: {len(bilingual)}",
        f"- Heuristic differences reviewed: {len(parity_warnings)}",
        "",
        "## Errors",
        "",
    ]
    bilingual_lines.extend([f"- {error}" for error in bilingual] or ["- None"])
    bilingual_lines.extend(["", "## Heuristic review list", ""])
    bilingual_lines.extend([f"- {warning}" for warning in parity_warnings] or ["- None"])
    bilingual_report.write_text("\n".join(bilingual_lines) + "\n", encoding="utf-8")

    errors = all_content_errors + bilingual
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Content and bilingual validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
