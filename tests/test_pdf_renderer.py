from pathlib import Path

from src.corpus import load_questions, validate_questions
from src.latex_renderer import build_tex


ROOT = Path(__file__).resolve().parents[1]


def _questions() -> list[dict]:
    questions = load_questions(ROOT / "content" / "questions.json")
    assert validate_questions(questions) == []
    return questions


def test_exercise_tex_uses_xetex_fonts_structured_math_and_safe_blanks() -> None:
    tex = build_tex(
        _questions(),
        language="zh",
        kind="exercises",
        chapter=1,
        pdf_title="test",
    )

    assert r"\setCJKmainfont{FandolSong-Regular.otf}" in tex
    assert r"\setsansfont{texgyreheros-regular.otf}" in tex
    assert r"\setmathfont{STIXTwoMath-Regular.otf}" in tex
    assert "includeheadfoot,headheight=5mm,headsep=3mm,footskip=6mm" in tex
    assert r"\frac{" in tex
    assert r"\begin{cases}" in tex
    assert "______" not in tex
    assert r"\underline{\qquad}" in tex
    assert r"\textbackslash{}frac" not in tex


def test_solution_tex_contains_every_question_and_real_math_environments() -> None:
    tex = build_tex(
        _questions(),
        language="en",
        kind="solutions",
        chapter=1,
        pdf_title="test",
    )

    for number in range(1, 101):
        assert f"solution-Q{number:03d}" in tex
    assert tex.count(r"\pdfbookmark[1]") == 100
    assert r"\(\lim_{" in tex
    assert r"\(\frac{" in tex
    assert r"\textbackslash{}varepsilon" not in tex
