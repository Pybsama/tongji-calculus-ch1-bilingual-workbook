from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


SECTION_QUOTAS = {1: 11, 2: 10, 3: 10, 4: 7, 5: 13, 6: 16, 7: 11, 8: 10, 9: 4, 10: 8}
TYPE_QUOTAS = {
    "single_choice": 10,
    "multiple_choice": 6,
    "true_false": 8,
    "fill_blank": 10,
    "calculation": 36,
    "proof": 18,
    "comprehensive": 8,
    "error_diagnosis": 4,
}
DIFFICULTY_QUOTAS = {
    "basic": 22,
    "standard": 33,
    "advanced": 27,
    "hard": 14,
    "challenge": 4,
}
VALID_TIERS = {"foundation", "methods", "synthesis", "challenge"}
VALID_SPACES = {"S", "M", "L", "XL"}
SOURCE_LINEAGE_CATEGORIES = {
    "open_text_adaptation",
    "classic_method_variant",
    "original_synthesis",
}
SOURCE_LINEAGE_REFERENCE_IDS = {
    "openstax-v1-1.1-functions",
    "openstax-v1-1.4-inverse-functions",
    "openstax-v1-2.2-function-limits",
    "openstax-v1-2.3-limit-laws",
    "openstax-v1-2.4-continuity",
    "openstax-v1-2.5-precise-limit",
    "openstax-v1-4.3-extrema",
    "openstax-v2-5.1-sequences",
    "mit-18.01sc-session-4-limits-continuity",
    "mit-18.01sc-session-5-discontinuity",
    "mit-18.01sc-session-8-trig-limits",
    "mit-18.01sc-session-19-limit-involving-e",
}
REQUIRED_LOCALIZED = {"title", "prompt", "answer", "solution"}
REQUIRED_SOLUTION = {
    "knowledge",
    "analysis",
    "steps",
    "pitfalls",
    "verification",
    "takeaway",
    "extension",
}


def load_questions(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, list):
        raise ValueError("Question corpus must be a JSON array.")
    return value


def _quota_errors(label: str, actual: Counter, expected: dict) -> list[str]:
    errors: list[str] = []
    for key, count in expected.items():
        if actual[key] != count:
            errors.append(f"{label} quota {key!r}: expected {count}, got {actual[key]}")
    extra = set(actual) - set(expected)
    if extra:
        errors.append(f"{label} has unsupported values: {sorted(extra)!r}")
    return errors


def validate_questions(items: list[dict[str, Any]], enforce_quotas: bool = True) -> list[str]:
    errors: list[str] = []
    if enforce_quotas and len(items) != 100:
        errors.append(f"Expected 100 questions, got {len(items)}")

    ids = [str(item.get("id", "")) for item in items]
    duplicates = sorted(item_id for item_id, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append(f"Duplicate IDs: {duplicates}")

    if enforce_quotas:
        expected_ids = [f"Q{index:03d}" for index in range(1, 101)]
        if ids != expected_ids:
            errors.append("IDs must be ordered exactly Q001-Q100")

    for index, item in enumerate(items, start=1):
        item_id = item.get("id", f"item-{index}")
        prefix = f"{item_id}: "
        required = {
            "id",
            "section",
            "tier",
            "difficulty",
            "type",
            "tags",
            "minutes",
            "space",
            "classic_method",
            "source_lineage",
            "zh",
            "en",
        }
        missing = sorted(required - set(item))
        if missing:
            errors.append(prefix + f"missing fields {missing}")
            continue
        if item["tier"] not in VALID_TIERS:
            errors.append(prefix + f"unsupported tier {item['tier']!r}")
        if item["space"] not in VALID_SPACES:
            errors.append(prefix + f"unsupported space {item['space']!r}")
        if not isinstance(item["minutes"], int) or not 2 <= item["minutes"] <= 45:
            errors.append(prefix + "minutes must be an integer from 2 through 45")
        if not isinstance(item["classic_method"], bool):
            errors.append(prefix + "classic_method must be boolean")

        lineage = item["source_lineage"]
        if not isinstance(lineage, dict):
            errors.append(prefix + "source_lineage must be an object")
        else:
            lineage_fields = {
                "category",
                "method_family",
                "relation",
                "references",
            }
            lineage_missing = sorted(lineage_fields - set(lineage))
            lineage_extra = sorted(set(lineage) - lineage_fields)
            if lineage_missing:
                errors.append(prefix + f"source_lineage missing {lineage_missing}")
            if lineage_extra:
                errors.append(prefix + f"source_lineage has unsupported fields {lineage_extra}")
            category = lineage.get("category")
            if category not in SOURCE_LINEAGE_CATEGORIES:
                errors.append(prefix + f"unsupported source_lineage category {category!r}")
            method_family = lineage.get("method_family")
            if not isinstance(method_family, str) or len(method_family.strip()) < 3:
                errors.append(prefix + "source_lineage method_family is too short")
            relation = lineage.get("relation")
            if not isinstance(relation, str) or len(relation.strip()) < 24:
                errors.append(prefix + "source_lineage relation is too short")
            references = lineage.get("references")
            if not isinstance(references, list) or not references:
                errors.append(prefix + "source_lineage references must be a non-empty array")
            elif not all(isinstance(reference, str) for reference in references):
                errors.append(prefix + "source_lineage references must contain strings")
            else:
                if len(references) != len(set(references)):
                    errors.append(prefix + "source_lineage references must be unique")
                unknown_references = sorted(set(references) - SOURCE_LINEAGE_REFERENCE_IDS)
                if unknown_references:
                    errors.append(
                        prefix
                        + f"source_lineage has unknown reference IDs {unknown_references}"
                    )

        tags = item["tags"]
        if not isinstance(tags, dict) or not tags.get("zh") or not tags.get("en"):
            errors.append(prefix + "tags must contain non-empty zh and en arrays")

        for language in ("zh", "en"):
            localized = item[language]
            if not isinstance(localized, dict):
                errors.append(prefix + f"{language} must be an object")
                continue
            localized_missing = sorted(REQUIRED_LOCALIZED - set(localized))
            if localized_missing:
                errors.append(prefix + f"{language} missing {localized_missing}")
                continue
            if not str(localized["prompt"]).strip():
                errors.append(prefix + f"{language} prompt is empty")
            if not str(localized["answer"]).strip():
                errors.append(prefix + f"{language} answer is empty")
            solution = localized["solution"]
            if not isinstance(solution, dict):
                errors.append(prefix + f"{language}.solution must be an object")
                continue
            solution_missing = sorted(REQUIRED_SOLUTION - set(solution))
            if solution_missing:
                errors.append(prefix + f"{language}.solution missing {solution_missing}")
                continue
            if len(solution["steps"]) < 2:
                errors.append(prefix + f"{language}.solution needs at least two steps")
            if not solution["knowledge"] or not solution["pitfalls"]:
                errors.append(prefix + f"{language}.solution knowledge/pitfalls cannot be empty")

        if item["type"] in {"single_choice", "multiple_choice"}:
            for language in ("zh", "en"):
                if len(item[language].get("choices", [])) < 4:
                    errors.append(prefix + f"{language} choice question needs at least four choices")

    if enforce_quotas:
        errors.extend(_quota_errors("section", Counter(item.get("section") for item in items), SECTION_QUOTAS))
        errors.extend(_quota_errors("type", Counter(item.get("type") for item in items), TYPE_QUOTAS))
        errors.extend(
            _quota_errors(
                "difficulty",
                Counter(item.get("difficulty") for item in items),
                DIFFICULTY_QUOTAS,
            )
        )
    return errors
