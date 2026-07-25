from __future__ import annotations

import sys
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.corpus import load_questions, validate_questions
from src.formula_semantics import audit_formula_semantics
from src.latex_renderer import compile_pdf
from src.math_markup import audit_text
from scripts.merge_corpus import main as merge_corpus
from scripts.migrate_latex import _localized_payload


CHAPTER = 1
OUTPUTS = {
    ("zh", "exercises"): "同济高数第七版_第一章_习题册_中文.pdf",
    ("zh", "solutions"): "同济高数第七版_第一章_超详细解析_中文.pdf",
    ("en", "exercises"): "Tongji_Calculus_7e_Chapter_1_Exercises_EN.pdf",
    ("en", "solutions"): "Tongji_Calculus_7e_Chapter_1_Detailed_Solutions_EN.pdf",
}


def _validate_katex() -> None:
    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError("Node.js/npm is required for the KaTeX compatibility audit.")
    if not (ROOT / "node_modules" / "katex" / "package.json").is_file():
        raise RuntimeError("Run `npm ci` before building so the pinned KaTeX audit is available.")
    completed = subprocess.run(
        [npm, "run", "--silent", "validate:katex"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            "KaTeX compatibility audit failed:\n"
            + completed.stdout
            + completed.stderr
        )
    print(completed.stdout.strip())


def _math_audit(value: object, path: str, errors: list[str]) -> None:
    if isinstance(value, str):
        errors.extend(f"{path}: {message}" for message in audit_text(value))
        errors.extend(
            f"{path}: {message}" for message in audit_formula_semantics(value)
        )
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _math_audit(item, f"{path}[{index}]", errors)
    elif isinstance(value, dict):
        for key, item in value.items():
            _math_audit(item, f"{path}.{key}", errors)


def main() -> int:
    if merge_corpus() != 0:
        return 1
    corpus_path = ROOT / "content" / "questions.json"
    questions = load_questions(corpus_path)
    errors = validate_questions(questions, enforce_quotas=True)
    for item in questions:
        _math_audit(item, item["id"], errors)
        if _localized_payload(item) != item:
            errors.append(f"{item['id']}: LaTeX migration is not idempotent")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    _validate_katex()
    dist = ROOT / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    for language in ("zh", "en"):
        exercise_path = dist / OUTPUTS[(language, "exercises")]
        solution_path = dist / OUTPUTS[(language, "solutions")]
        print(f"Building {exercise_path.name}")
        compile_pdf(
            questions,
            language=language,
            kind="exercises",
            chapter=CHAPTER,
            output_path=exercise_path,
            root=ROOT,
        )
        print(f"Building {solution_path.name}")
        compile_pdf(
            questions,
            language=language,
            kind="solutions",
            chapter=CHAPTER,
            output_path=solution_path,
            root=ROOT,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
