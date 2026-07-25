from src.math_markup import audit_text, auto_markup_text, normalize_latex


def test_audit_text_requires_explicit_latex_for_formula() -> None:
    assert audit_text("设 $f(x)=x^2$。") == []

    errors = audit_text("设 f(x)=x²。")

    assert any("outside LaTeX delimiters" in error for error in errors)


def test_audit_text_rejects_unicode_math_shortcuts_inside_formula() -> None:
    errors = audit_text("$aₙ=(-1)ⁿ/n$")

    assert any("Unicode math shortcut" in error for error in errors)


def test_audit_text_rejects_slash_style_division_inside_formula() -> None:
    errors = audit_text(r"$[f(x+h)-f(x)]/h$")

    assert any("slash-style division" in error for error in errors)


def test_auto_markup_text_converts_a_chinese_function_formula() -> None:
    assert auto_markup_text("函数 f(x)=√(2-x)+ln(x+1) 的定义域") == (
        r"函数 $f(x)=\sqrt{2-x}+\ln(x+1)$ 的定义域"
    )


def test_auto_markup_text_is_idempotent() -> None:
    once = auto_markup_text("As x→0, f(x)=x².")

    assert auto_markup_text(once) == once


def test_normalize_latex_builds_structural_fractions() -> None:
    assert normalize_latex(r"\lim_{x\to0}\sin(5x)/(3x)") == (
        r"\lim_{x\to0}\frac{\sin(5x)}{3x}"
    )
    assert normalize_latex(r"|a_n|/n=1/n") == (
        r"\frac{|a_n|}{n}=\frac{1}{n}"
    )


def test_normalize_latex_handles_nested_and_chained_division() -> None:
    assert normalize_latex(r"\sin(1/x)") == r"\sin(\frac{1}{x})"
    assert normalize_latex(r"a/b/c") == r"\frac{\frac{a}{b}}{c}"


def test_normalize_latex_preserves_absolute_value_operands() -> None:
    assert normalize_latex(r"h(-x)=|-x|/(1+(-x)^2)") == (
        r"h(-x)=\frac{|-x|}{1+(-x)^2}"
    )
    assert normalize_latex(r"|(3n-2)/(n+1)-3|") == (
        r"|\frac{3n-2}{n+1}-3|"
    )
    assert normalize_latex(r"|b-ac|/|n+c|") == (
        r"\frac{|b-ac|}{|n+c|}"
    )
    assert normalize_latex(r"|(3n-2-3n-3)/(n+1)|=5/(n+1)") == (
        r"|\frac{3n-2-3n-3}{n+1}|=\frac{5}{n+1}"
    )
    assert normalize_latex(r"|1/\alpha(x)|\to\infty") == (
        r"|\frac{1}{\alpha(x)}|\to\infty"
    )


def test_normalize_latex_preserves_floors_ceilings_and_literal_braces() -> None:
    assert normalize_latex(r"\lceil 5/\varepsilon\rceil") == (
        r"\lceil\frac{5}{\varepsilon}\rceil"
    )
    assert normalize_latex(r"\min\{1,\varepsilon/(2|a|+1)\}") == (
        r"\min\{1,\frac{\varepsilon}{2|a|+1}\}"
    )


def test_normalize_latex_canonicalizes_legacy_limit_subscripts() -> None:
    assert normalize_latex(
        r"\lim_(n\to\infty) (5n^2-3n+1)/(2n^2+n-4)"
    ) == (
        r"\lim_{n\to\infty} \frac{5n^2-3n+1}{2n^2+n-4}"
    )
    assert normalize_latex(r"\lim_{x\to0^-}|x|/x") == (
        r"\lim_{x\to0^-}\frac{|x|}{x}"
    )
    assert normalize_latex(r"\lim_{x\to0^{-}}|x|/x") == (
        r"\lim_{x\to0^{-}}\frac{|x|}{x}"
    )


def test_normalize_latex_preserves_fraction_idempotently() -> None:
    value = r"\frac{x^2-1}{x-1}"

    assert normalize_latex(value) == value


def test_normalize_latex_preserves_inverse_trigonometric_function_names() -> None:
    assert normalize_latex("arcsin x") == r"\arcsin x"
    assert normalize_latex("arccos x") == r"\arccos x"
    assert normalize_latex("arctan x") == r"\arctan x"
    assert normalize_latex("xsin x") == r"x\sin x"


def test_normalize_latex_preserves_literal_set_braces() -> None:
    assert normalize_latex("X={-1,0,1}") == r"X=\{-1,0,1\}"
    assert normalize_latex("{0,1,2}") == r"\{0,1,2\}"
    assert normalize_latex("{a_n}") == r"\{a_n\}"
    assert normalize_latex("{(-1,1),(0,0),(1,1)}") == (
        r"\{(-1,1),(0,0),(1,1)\}"
    )
    assert normalize_latex(r"\min{1,\frac{\varepsilon}{5}}") == (
        r"\min\{1,\frac{\varepsilon}{5}\}"
    )


def test_auto_markup_merges_adjacent_math_fragments() -> None:
    assert auto_markup_text(r"由 $T=k$$\pi$ 得证。") == r"由 $T=k\pi$ 得证。"


def test_auto_markup_merges_floor_notation_with_neighboring_math() -> None:
    assert auto_markup_text(r"证明 $\lim_{x\to\infty}$⌊x⌋$/x=1$。") == (
        r"证明 $\lim_{x\to\infty}\frac{\lfloor x\rfloor}{x}=1$。"
    )


def test_auto_markup_merges_factorial_and_differential_fragments() -> None:
    assert auto_markup_text(r"有 $(-1)^n n$!$/x^n$。") == (
        r"有 $\frac{(-1)^n n!}{x^n}$。"
    )
    assert auto_markup_text(r"求 dθ$/dt$。") == (
        r"求 $\frac{d\theta}{dt}$。"
    )
    assert auto_markup_text(r"角速度为 $-0.075$ rad$/s$。") == (
        r"角速度为 $-0.075\,\frac{\mathrm{rad}}{s}$。"
    )


def test_auto_markup_converts_equivalence_cube_roots_and_ellipsis() -> None:
    assert auto_markup_text("若 α∼β，则比值趋于 1。") == (
        r"若 $\alpha \sim \beta$，则比值趋于 1。"
    )
    assert auto_markup_text("令 u=∛x。") == r"令 $u=\sqrt[3]{x}$。"
    assert auto_markup_text("H_m=1+1/2+⋯+1/m") == (
        r"$H_m=1+\frac{1}{2}+\cdots +\frac{1}{m}$"
    )
    assert auto_markup_text("√10001") == r"$\sqrt{10001}$"


def test_auto_markup_converts_unicode_prime_runs_without_fragmenting_math() -> None:
    assert auto_markup_text("y‴=24x") == r"$y'''=24x$"
    assert auto_markup_text("f'=u'v+uv′") == r"$f'=u'v+uv'$"
    assert auto_markup_text("当 x→a 时 f(x)→AB。") == (
        r"当 $x\to a$ 时 $f(x)\to AB$。"
    )
    assert auto_markup_text("1±ax") == r"$1\pm ax$"


def test_normalize_latex_uses_superscripts_for_one_sided_limits() -> None:
    assert normalize_latex(r"\lim_{x\to 0+}f(x)") == (
        r"\lim_{x\to 0^{+}}f(x)"
    )
    assert normalize_latex(r"\lim_{x\to a-}f(x)") == (
        r"\lim_{x\to a^{-}}f(x)"
    )
    assert normalize_latex(r"x\to 0+,\frac{1}{x}\to+\infty") == (
        r"x\to 0^{+},\frac{1}{x}\to+\infty"
    )


def test_auto_markup_converts_a_standalone_multiplication_sign() -> None:
    assert audit_text("振幅 × 有界") != []
    assert auto_markup_text("振幅 × 有界") == r"振幅 $\times$ 有界"


def test_auto_markup_converts_quantifiers_number_sets_and_ell() -> None:
    assert auto_markup_text("∀ε>0，∃N∈ℕ。") == (
        r"$\forall \varepsilon >0$，$\exists N\in \mathbb{N}$。"
    )
    assert auto_markup_text("设其极限为 ℓ。") == r"设其极限为 $\ell$。"


def test_auto_markup_rewrites_circled_enumerators_to_portable_text() -> None:
    assert auto_markup_text("证明：① 有界；② 单调。") == "证明：（1） 有界；（2） 单调。"


def test_auto_markup_does_not_swallow_english_prose_boundaries() -> None:
    assert auto_markup_text("At x=0, the formula gives 1.") == (
        r"At $x=0$, the formula gives 1."
    )
    assert auto_markup_text("The student's n=1 formula is wrong.") == (
        r"The student's $n=1$ formula is wrong."
    )
    assert auto_markup_text("epsilon-N and stage-by-stage") == (
        "epsilon-N and stage-by-stage"
    )
    assert auto_markup_text(r"L'Hôpital's rule") == r"L'Hôpital's rule"
    assert auto_markup_text("a 1^∞ form") == r"a $1^\infty$ form"
    assert auto_markup_text("For A, sin x∼x.") == (
        r"For A, $\sin x\sim x$."
    )
    assert auto_markup_text("an ε-neighborhood of A") == (
        r"an $\varepsilon$-neighborhood of A"
    )
    assert auto_markup_text("no 0⁰-type competition") == (
        r"no $0^{0}$-type competition"
    )
    assert auto_markup_text("proof of an if-and-only-if statement") == (
        "proof of an if-and-only-if statement"
    )


def test_auto_markup_normalizes_answer_blanks_inside_and_outside_math() -> None:
    assert auto_markup_text("答案为 ______。") == (
        r"答案为 $\underline{\qquad}$。"
    )
    assert auto_markup_text(r"$f(x)=____$。") == (
        r"$f(x)=\underline{\qquad}$。"
    )
    assert auto_markup_text("a ____-order infinitesimal") == (
        r"a $\underline{\qquad}$-order infinitesimal"
    )


def test_auto_markup_keeps_dom_and_range_with_their_formulas() -> None:
    assert auto_markup_text(
        r"Dom$(f^{-1})=[-1,5]$，Range$(f^{-1})=[1,4]$。"
    ) == (
        r"$\operatorname{Dom}(f^{-1})=[-1,5]$，"
        r"$\operatorname{Range}(f^{-1})=[1,4]$。"
    )


def test_real_number_set_uses_explicit_mathbb_group() -> None:
    assert auto_markup_text(r"$x\in R$") == r"$x\in \mathbb{R}$"
    assert auto_markup_text(r"$f:\mathbb R\to\mathbb R$") == (
        r"$f:\mathbb{R}\to\mathbb{R}$"
    )


def test_audit_rejects_superscript_letters_outside_math() -> None:
    assert audit_text("A. 2xeˣ") != []


def test_auto_markup_converts_mapsto_and_merges_adjacent_formula() -> None:
    assert auto_markup_text(r"外层是 u↦$u^{5}$。") == (
        r"外层是 $u\mapsto u^{5}$。"
    )
