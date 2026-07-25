import json
from pathlib import Path

from src.corpus import (
    DIFFICULTY_QUOTAS,
    SECTION_QUOTAS,
    SOURCE_LINEAGE_CATEGORIES,
    SOURCE_LINEAGE_REFERENCE_IDS,
    TYPE_QUOTAS,
    load_questions,
    validate_questions,
)


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "content" / "questions.json"
PARTS = ROOT / "content" / "parts"
SCHEMA = ROOT / "content" / "schema.json"
SOURCES = ROOT / "SOURCES.md"


def test_quota_totals_are_one_hundred() -> None:
    assert sum(SECTION_QUOTAS.values()) == 100
    assert sum(TYPE_QUOTAS.values()) == 100
    assert sum(DIFFICULTY_QUOTAS.values()) == 100


def test_final_corpus_is_complete_and_valid() -> None:
    assert CORPUS.exists(), "Run scripts/merge_corpus.py after authoring all three parts."
    questions = load_questions(CORPUS)
    assert validate_questions(questions, enforce_quotas=True) == []


def test_every_question_has_honest_source_lineage() -> None:
    questions = load_questions(CORPUS)
    categories = set()
    for item in questions:
        lineage = item["source_lineage"]
        assert set(lineage) == {
            "category",
            "method_family",
            "relation",
            "references",
        }
        categories.add(lineage["category"])
        assert lineage["category"] in SOURCE_LINEAGE_CATEGORIES
        assert len(lineage["method_family"].strip()) >= 3
        assert len(lineage["relation"].strip()) >= 24
        assert lineage["references"]
        assert set(lineage["references"]) <= SOURCE_LINEAGE_REFERENCE_IDS
        assert not any(
            protected_name in lineage["relation"].lower()
            for protected_name in ("tongji", "stewart", "thomas")
        )
    assert categories == SOURCE_LINEAGE_CATEGORIES


def test_lineage_is_present_in_authoring_parts_and_documented() -> None:
    authored = [
        item
        for path in sorted(PARTS.glob("sections_*.json"))
        for item in load_questions(path)
    ]
    assert len(authored) == 100
    assert all("source_lineage" in item for item in authored)

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    schema_reference_ids = set(
        schema["properties"]["source_lineage"]["properties"]["references"]["items"][
            "enum"
        ]
    )
    assert schema_reference_ids == SOURCE_LINEAGE_REFERENCE_IDS

    source_document = SOURCES.read_text(encoding="utf-8")
    for reference_id in SOURCE_LINEAGE_REFERENCE_IDS:
        assert f"`{reference_id}`" in source_document
