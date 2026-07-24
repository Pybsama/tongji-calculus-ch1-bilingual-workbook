from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.corpus import load_questions, validate_questions
from src.pdf_renderer import build_exercises, build_solutions


OUTPUTS = {
    ("zh", "exercises"): "同济高数第七版_第一章_习题册_中文.pdf",
    ("zh", "solutions"): "同济高数第七版_第一章_超详细解析_中文.pdf",
    ("en", "exercises"): "Tongji_Calculus_7e_Chapter_1_Exercises_EN.pdf",
    ("en", "solutions"): "Tongji_Calculus_7e_Chapter_1_Detailed_Solutions_EN.pdf",
}


def main() -> int:
    corpus_path = ROOT / "content" / "questions.json"
    questions = load_questions(corpus_path)
    errors = validate_questions(questions, enforce_quotas=True)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    dist = ROOT / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    for language in ("zh", "en"):
        exercise_path = dist / OUTPUTS[(language, "exercises")]
        solution_path = dist / OUTPUTS[(language, "solutions")]
        print(f"Building {exercise_path.name}")
        build_exercises(questions, language, exercise_path)
        print(f"Building {solution_path.name}")
        build_solutions(questions, language, solution_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

