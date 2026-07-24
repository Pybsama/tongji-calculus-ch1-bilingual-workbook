from pathlib import Path

from src.bilingual_checks import bilingual_warnings, validate_bilingual
from src.corpus import load_questions


ROOT = Path(__file__).resolve().parents[1]


def test_chinese_and_english_mathematics_match() -> None:
    questions = load_questions(ROOT / "content" / "questions.json")
    assert validate_bilingual(questions) == []


def test_bilingual_symbol_warnings_are_deterministic() -> None:
    item = {
        "zh": {
            "prompt": "ε→∞",
            "answer": "",
            "solution": {"steps": ["ε→∞"]},
        },
        "en": {
            "prompt": "",
            "answer": "",
            "solution": {"steps": [""]},
        },
    }
    warnings = bilingual_warnings(item)
    symbol_warnings = [warning for warning in warnings if warning.startswith("symbol")]
    assert symbol_warnings == sorted(symbol_warnings)
