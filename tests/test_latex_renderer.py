from src.latex_renderer import _question_heading, bookmark_text, latex_text


def test_latex_text_preserves_math_and_escapes_prose() -> None:
    assert latex_text(r"正确率 80%，且 $f(x)=\frac{1}{x}$。") == (
        r"正确率 80\%，且 \(f(x)=\frac{1}{x}\)。"
    )


def test_latex_text_renders_answer_blanks_inside_math_safely() -> None:
    rendered = latex_text(r"$v(3)=\underline{\qquad}$")

    assert rendered == r"\(v(3)=\underline{\qquad}\)"
    assert "______" not in rendered


def test_bookmark_text_removes_tex_commands_without_exposing_source() -> None:
    assert bookmark_text(r"用 $\varepsilon-\delta$ 定义证明") == "用 ε-δ 定义证明"
    assert bookmark_text(r"$f(x)=\frac{1}{x}$") == "f(x)=1/x"


def test_question_heading_uses_lineage_category_not_legacy_flag() -> None:
    item = {
        "difficulty": "hard",
        "type": "error_diagnosis",
        "tier": "challenge",
        "classic_method": True,
        "source_lineage": {"category": "original_synthesis"},
    }

    heading = _question_heading(item, language="zh")

    assert "原创综合 / 诊断" in heading
    assert "经典方法变式" not in heading
