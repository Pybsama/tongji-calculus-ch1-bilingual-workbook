from src.formula_semantics import audit_formula_semantics


def test_rejects_known_migration_artifacts() -> None:
    examples = (
        r"$y=\arc\tan x$",
        r"$\Sigma_{k=1}^{n} k$",
        r"$\sqrt{}$",
        r"$\sqrt{0.2}5$",
        r"$x\to 0+$",
        r"$v(3)=______$",
        r"$x=$",
    )

    for example in examples:
        assert audit_formula_semantics(example), example


def test_accepts_canonical_katex_compatible_forms() -> None:
    examples = (
        r"$y=\arctan x$",
        r"$\sum_{k=1}^{n} k$",
        r"$\sqrt{0.25}$",
        r"$x\to 0^{+}$",
        r"$v(3)=\underline{\qquad}$",
    )

    for example in examples:
        assert audit_formula_semantics(example) == [], example
