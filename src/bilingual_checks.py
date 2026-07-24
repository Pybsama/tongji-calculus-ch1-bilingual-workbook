from __future__ import annotations

import re
from collections import Counter


NUMBER_PATTERN = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?:/\d+)?")
MATH_SYMBOLS = "∞√εδεδ→≥≤≠∪∩±"


def _numbers(text: str) -> Counter[str]:
    return Counter(NUMBER_PATTERN.findall(text.replace("−", "-")))


def _symbols(text: str) -> Counter[str]:
    return Counter(character for character in text if character in MATH_SYMBOLS)


def check_bilingual_math(item: dict) -> list[str]:
    """Return hard bilingual consistency errors for one question."""
    errors: list[str] = []
    zh = item["zh"]
    en = item["en"]
    if len(zh.get("choices", [])) != len(en.get("choices", [])):
        errors.append("choice counts differ")

    zh_steps = zh["solution"]["steps"]
    en_steps = en["solution"]["steps"]
    if len(zh_steps) != len(en_steps):
        errors.append(f"solution step counts differ: zh={len(zh_steps)}, en={len(en_steps)}")
    return errors


def bilingual_warnings(item: dict) -> list[str]:
    """Return heuristic parity differences that require human review."""
    warnings: list[str] = []
    zh = item["zh"]
    en = item["en"]
    for field in ("prompt", "answer"):
        zh_numbers = _numbers(str(zh.get(field, "")))
        en_numbers = _numbers(str(en.get(field, "")))
        if zh_numbers != en_numbers:
            warnings.append(
                f"{field} numeric tokens differ: zh={dict(zh_numbers)}, en={dict(en_numbers)}"
            )
    zh_steps = zh["solution"]["steps"]
    en_steps = en["solution"]["steps"]
    zh_core = " ".join([zh["prompt"], zh["answer"], *zh_steps])
    en_core = " ".join([en["prompt"], en["answer"], *en_steps])
    zh_symbols = _symbols(zh_core)
    en_symbols = _symbols(en_core)
    for symbol in sorted(set(zh_symbols) | set(en_symbols)):
        if abs(zh_symbols[symbol] - en_symbols[symbol]) > 1:
            warnings.append(
                f"symbol {symbol!r} count differs materially: zh={zh_symbols[symbol]}, en={en_symbols[symbol]}"
            )
    return warnings


def validate_bilingual(items: list[dict]) -> list[str]:
    errors: list[str] = []
    for item in items:
        for error in check_bilingual_math(item):
            errors.append(f"{item['id']}: {error}")
    return errors
