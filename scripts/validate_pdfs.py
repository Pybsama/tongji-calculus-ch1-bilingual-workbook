from __future__ import annotations

from collections import Counter
import hashlib
from pathlib import Path
import re
import sys
from typing import Any, Iterable

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_pdfs import OUTPUTS
from src.corpus import load_questions
from src.formula_semantics import audit_formula_semantics
from src.math_markup import audit_text


DIST = ROOT / "dist"
REPORT = ROOT / "reports" / "pdf_validation.md"
CHECKSUMS = ROOT / "SHA256SUMS"
EXPECTED_SIZE_MM = {"exercises": (264.0, 198.0), "solutions": (198.0, 264.0)}
REQUIRED_FONT_FAMILIES = ("TeXGyreHeros", "STIXTwoMath")
FORBIDDEN_FONT_FAMILIES = ("LMSans",)
FORBIDDEN_ACTIONS = {
    "/ImportData",
    "/JavaScript",
    "/Launch",
    "/Movie",
    "/Rendition",
    "/Sound",
    "/SubmitForm",
}
FORBIDDEN_ANNOTATIONS = {
    "/3D",
    "/FileAttachment",
    "/Movie",
    "/RichMedia",
    "/Screen",
    "/Sound",
}


def _points_to_mm(value: float) -> float:
    return value * 25.4 / 72.0


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _checksum_entries() -> tuple[dict[str, str], list[str]]:
    if not CHECKSUMS.is_file():
        return {}, ["Missing SHA256SUMS"]
    entries: dict[str, str] = {}
    errors: list[str] = []
    for line_number, line in enumerate(
        CHECKSUMS.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        match = re.fullmatch(r"([0-9a-f]{64})  dist/(.+)", line)
        if match is None:
            errors.append(f"SHA256SUMS:{line_number}: malformed entry")
            continue
        digest, name = match.groups()
        if name in entries:
            errors.append(f"SHA256SUMS:{line_number}: duplicate entry for {name}")
        entries[name] = digest
    expected_names = set(OUTPUTS.values())
    actual_names = set(entries)
    missing = sorted(expected_names - actual_names)
    unexpected = sorted(actual_names - expected_names)
    if missing or unexpected:
        errors.append(
            f"SHA256SUMS release set mismatch: missing={missing}, unexpected={unexpected}"
        )
    return entries, errors


def _outline_titles(entries: Iterable[Any]) -> list[str]:
    titles: list[str] = []
    for entry in entries:
        if isinstance(entry, list):
            titles.extend(_outline_titles(entry))
            continue
        title = getattr(entry, "title", None)
        if title is not None:
            titles.append(str(title))
    return titles


def _resolved(value: Any) -> Any:
    return value.get_object() if hasattr(value, "get_object") else value


def _font_records(reader: PdfReader) -> list[tuple[str, bool | None]]:
    records: dict[tuple[str, bool | None], None] = {}
    visited: set[int] = set()

    def visit(font: Any) -> None:
        resolved = _resolved(font)
        identity = id(resolved)
        if identity in visited or not hasattr(resolved, "get"):
            return
        visited.add(identity)
        name = str(resolved.get("/BaseFont", "(unnamed)")).lstrip("/")
        descriptor = _resolved(resolved.get("/FontDescriptor"))
        embedded: bool | None = None
        if hasattr(descriptor, "get"):
            embedded = any(
                descriptor.get(key) is not None
                for key in ("/FontFile", "/FontFile2", "/FontFile3")
            )
        records[(name, embedded)] = None
        descendants = _resolved(resolved.get("/DescendantFonts"))
        if isinstance(descendants, list):
            for descendant in descendants:
                visit(descendant)

    for page in reader.pages:
        resources = _resolved(page.get("/Resources"))
        fonts = _resolved(resources.get("/Font")) if hasattr(resources, "get") else None
        if hasattr(fonts, "values"):
            for font in fonts.values():
                visit(font)
    return sorted(records, key=lambda record: (record[0], str(record[1])))


def _walk_strings(value: Any, path: str = "root") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_strings(child, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from _walk_strings(child, f"{path}.{key}")


def _validate_source_math() -> list[str]:
    questions = load_questions(ROOT / "content" / "questions.json")
    errors: list[str] = []
    for index, item in enumerate(questions):
        for path, text in _walk_strings(item, f"Q{index + 1:03d}"):
            for message in audit_text(text):
                errors.append(f"{path}: {message}")
            for message in audit_formula_semantics(text):
                errors.append(f"{path}: {message}")
    return errors


def _page_stream_size(page: Any) -> int:
    contents = page.get_contents()
    if contents is None:
        return 0
    try:
        return len(contents.get_data())
    except AttributeError:
        return 0


def _security_issues(reader: PdfReader) -> list[str]:
    issues: list[str] = []
    if reader.is_encrypted:
        issues.append("PDF is encrypted")
        return issues
    root = _resolved(reader.trailer.get("/Root"))
    if hasattr(root, "get"):
        for key in ("/AcroForm", "/AA"):
            if root.get(key) is not None:
                issues.append(f"catalog contains {key}")
        open_action = _resolved(root.get("/OpenAction"))
        if open_action is not None and not isinstance(open_action, list):
            issues.append("catalog contains a non-destination /OpenAction")
        names = _resolved(root.get("/Names"))
        if hasattr(names, "get"):
            for key in ("/EmbeddedFiles", "/JavaScript"):
                if names.get(key) is not None:
                    issues.append(f"name tree contains {key}")
    for page_number, page in enumerate(reader.pages, start=1):
        if page.get("/AA") is not None:
            issues.append(f"page {page_number} contains additional actions")
        annotations = _resolved(page.get("/Annots"))
        if not isinstance(annotations, list):
            continue
        for annotation in annotations:
            resolved = _resolved(annotation)
            if not hasattr(resolved, "get"):
                continue
            subtype = str(resolved.get("/Subtype", ""))
            if subtype in FORBIDDEN_ANNOTATIONS:
                issues.append(f"page {page_number} contains {subtype} annotation")
            action = _resolved(resolved.get("/A"))
            action_type = str(action.get("/S", "")) if hasattr(action, "get") else ""
            if action_type in FORBIDDEN_ACTIONS:
                issues.append(f"page {page_number} contains {action_type} action")
    metadata = reader.metadata or {}
    metadata_text = "\n".join(str(value) for value in metadata.values())
    if "/Users/" in metadata_text or "\\Users\\" in metadata_text:
        issues.append("metadata contains an absolute user path")
    return issues


def main() -> int:
    source_errors = _validate_source_math()
    errors = list(source_errors)
    checksum_entries, checksum_errors = _checksum_entries()
    errors.extend(checksum_errors)
    report_lines = [
        "# PDF validation",
        "",
        "- Renderer: XeTeX through pinned Tectonic bundle",
        f"- Source-math audit errors: {len(source_errors)}",
        f"- SHA256SUMS entries: {len(checksum_entries)} / {len(OUTPUTS)}",
        "",
    ]

    for (language, kind), name in OUTPUTS.items():
        path = DIST / name
        if not path.is_file():
            errors.append(f"Missing PDF: {name}")
            continue

        reader = PdfReader(path)
        security_issues = _security_issues(reader)
        if security_issues:
            errors.append(f"{name}: unsafe PDF features: {security_issues}")
        actual_digest = _sha256(path)
        expected_digest = checksum_entries.get(name)
        if expected_digest is not None and expected_digest != actual_digest:
            errors.append(
                f"{name}: SHA256SUMS mismatch: {expected_digest} != {actual_digest}"
            )
        expected_width, expected_height = EXPECTED_SIZE_MM[kind]
        wrong_sizes: list[str] = []
        blank_streams: list[int] = []
        for page_number, page in enumerate(reader.pages, start=1):
            width = _points_to_mm(float(page.mediabox.width))
            height = _points_to_mm(float(page.mediabox.height))
            if abs(width - expected_width) > 0.5 or abs(height - expected_height) > 0.5:
                wrong_sizes.append(f"{page_number}:{width:.1f}x{height:.1f}")
            if _page_stream_size(page) == 0:
                blank_streams.append(page_number)

        expected_pages = 102 if kind == "exercises" else None
        if expected_pages is not None and len(reader.pages) != expected_pages:
            errors.append(f"{name}: expected {expected_pages} pages, found {len(reader.pages)}")
        if kind == "solutions" and len(reader.pages) < 102:
            errors.append(f"{name}: solution PDF has only {len(reader.pages)} pages")
        exercise_id_errors: list[str] = []
        if kind == "exercises" and len(reader.pages) == 102:
            for number in range(1, 101):
                expected_id = f"Q{number:03d}"
                extracted = reader.pages[number + 1].extract_text() or ""
                if expected_id not in extracted:
                    exercise_id_errors.append(expected_id)
            if exercise_id_errors:
                errors.append(
                    f"{name}: question ID absent from expected exercise pages: "
                    f"{exercise_id_errors}"
                )
        if wrong_sizes:
            errors.append(f"{name}: wrong page sizes {wrong_sizes[:10]}")
        if blank_streams:
            errors.append(f"{name}: empty page content streams {blank_streams}")

        try:
            outline_titles = _outline_titles(reader.outline)
        except Exception as exc:  # pragma: no cover - defensive PDF parser boundary
            outline_titles = []
            errors.append(f"{name}: outline could not be read: {exc}")
        question_ids = [
            match.group(1)
            for title in outline_titles
            if (match := re.match(r"^(Q\d{3})\b", title))
        ]
        counts = Counter(question_ids)
        expected_ids = [f"Q{number:03d}" for number in range(1, 101)]
        missing_ids = [question_id for question_id in expected_ids if counts[question_id] == 0]
        duplicate_ids = [question_id for question_id, count in counts.items() if count != 1]
        unexpected_ids = sorted(set(question_ids) - set(expected_ids))
        if missing_ids or duplicate_ids or unexpected_ids:
            errors.append(
                f"{name}: bookmark IDs missing={missing_ids}, "
                f"duplicates={duplicate_ids}, unexpected={unexpected_ids}"
            )

        metadata = reader.metadata or {}
        creator = str(metadata.get("/Creator", ""))
        producer = str(metadata.get("/Producer", ""))
        if "LaTeX" not in creator:
            errors.append(f"{name}: Creator does not identify LaTeX: {creator!r}")
        if "xdvipdfmx" not in producer:
            errors.append(f"{name}: Producer does not identify xdvipdfmx: {producer!r}")

        fonts = _font_records(reader)
        font_names = sorted({name for name, _ in fonts})
        required_families = REQUIRED_FONT_FAMILIES + (("Fandol",) if language == "zh" else ())
        missing_families = [
            family for family in required_families if not any(family in name for name in font_names)
        ]
        forbidden_families = [
            family for family in FORBIDDEN_FONT_FAMILIES if any(family in name for name in font_names)
        ]
        unembedded = sorted(name for name, embedded in fonts if embedded is False)
        if missing_families:
            errors.append(f"{name}: required font families absent: {missing_families}")
        if forbidden_families:
            errors.append(f"{name}: forbidden fallback fonts present: {forbidden_families}")
        if unembedded:
            errors.append(f"{name}: unembedded fonts: {unembedded}")

        report_lines.extend(
            [
                f"## {name}",
                "",
                f"- Language / kind: `{language}` / `{kind}`",
                f"- Pages: {len(reader.pages)}",
                f"- Page size target: {expected_width:.0f} × {expected_height:.0f} mm",
                f"- Question bookmarks: {len(question_ids)} / 100",
                f"- Empty content streams: {blank_streams or 'None'}",
                f"- Exercise pages missing expected Q ID: {exercise_id_errors or 'None'}",
                f"- Security/attachment issues: {security_issues or 'None'}",
                f"- Fonts: `{', '.join(font_names)}`",
                f"- Creator: `{creator}`",
                f"- Producer: `{producer}`",
                f"- File size: {path.stat().st_size:,} bytes",
                f"- SHA-256: `{actual_digest}`",
                "",
            ]
        )

    report_lines.extend(["## Errors", ""])
    report_lines.extend([f"- {error}" for error in errors] or ["- None"])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("PDF validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
