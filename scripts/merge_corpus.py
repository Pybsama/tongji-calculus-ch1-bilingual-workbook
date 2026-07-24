from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.corpus import validate_questions


def main() -> int:
    part_paths = sorted((ROOT / "content" / "parts").glob("sections_*.json"))
    if not part_paths:
        print("No content parts found.", file=sys.stderr)
        return 1

    items: list[dict] = []
    for path in part_paths:
        with path.open("r", encoding="utf-8") as handle:
            part = json.load(handle)
        if not isinstance(part, list):
            print(f"{path} is not a JSON array.", file=sys.stderr)
            return 1
        items.extend(part)

    tier_order = {"foundation": 0, "methods": 1, "synthesis": 2, "challenge": 3}
    difficulty_order = {"basic": 0, "standard": 1, "advanced": 2, "hard": 3, "challenge": 4}
    items.sort(
        key=lambda item: (
            tier_order[item["tier"]],
            difficulty_order[item["difficulty"]],
            item["section"],
            item["id"],
        )
    )
    for index, item in enumerate(items, start=1):
        item["id"] = f"Q{index:03d}"
    errors = validate_questions(items, enforce_quotas=True)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    output = ROOT / "content" / "questions.json"
    output.write_text(
        json.dumps(items, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(items)} questions to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
