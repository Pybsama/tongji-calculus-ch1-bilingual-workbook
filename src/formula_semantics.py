from __future__ import annotations

import re


_FORMULA_PATTERNS = (
    (re.compile(r"\\arc\\(?:sin|cos|tan)\b"), "broken inverse-trigonometric command"),
    (
        re.compile(r"\\Sigma(?![A-Za-z])"),
        r"use \sum rather than the Greek-letter command \Sigma",
    ),
    (re.compile(r"\\sqrt\{\}"), "empty radical"),
    (
        re.compile(r"\\sqrt\{(?:\d+(?:\.\d+)?)\}(?:\d|\.)"),
        "numeric radical appears to stop before the full radicand",
    ),
    (
        re.compile(
            r"\\to\s*(?:-?\d+(?:\.\d+)?|[A-Za-z])[+-]"
            r"(?=\s*(?:[,;:，；：}]|$|\\))"
        ),
        "one-sided limit sign must be a superscript",
    ),
)


def _math_segments(text: str) -> list[str]:
    pieces = text.split("$")
    if len(pieces) % 2 == 0:
        return []
    return pieces[1::2]


def audit_formula_semantics(text: str) -> list[str]:
    """Catch high-risk migration artifacts that valid TeX can still typeset."""

    errors: list[str] = []
    if re.search(r"_{3,}", text):
        errors.append(r"raw answer blank; use $\underline{\qquad}$")
    if re.search(r"(?:epsilon|varepsilon)\$-[A-Za-z]\$", text):
        errors.append("definition name is split across math/prose boundaries")
    for formula in _math_segments(text):
        for pattern, message in _FORMULA_PATTERNS:
            if pattern.search(formula):
                errors.append(f"{message}: {formula!r}")
        if re.match(r"\s*[,;:，；：]", formula):
            errors.append(f"formula starts with punctuation: {formula!r}")
        terminal_superscript = re.search(r"\^(?:\{[+-]\}|[+-])\s*$", formula)
        if (
            re.search(r"(?:\\to|=|[+\-*/^_])\s*$", formula)
            and terminal_superscript is None
        ):
            errors.append(f"formula ends with an incomplete operator: {formula!r}")
    return errors
