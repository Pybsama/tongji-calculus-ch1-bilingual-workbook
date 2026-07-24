from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RENDER_ROOT = ROOT / "work" / "rendered_final"
REPORT = ROOT / "reports" / "pdf_validation.md"
SECTION_MARKER = "## Full-page render and pixel QA"


@dataclass
class RenderResult:
    name: str
    pages: int
    dimensions: set[tuple[int, int]]
    edge_hits: list[int]
    sparse_pages: list[int]


def _render(pdf: Path) -> list[Path]:
    output_dir = RENDER_ROOT / pdf.stem
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    prefix = output_dir / "page"
    subprocess.run(
        ["pdftoppm", "-png", "-r", "72", str(pdf), str(prefix)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    return sorted(output_dir.glob("page-*.png"))


def _inspect(pdf: Path) -> RenderResult:
    pages = _render(pdf)
    edge_hits: list[int] = []
    sparse_pages: list[int] = []
    dimensions: set[tuple[int, int]] = set()
    for page_number, image_path in enumerate(pages, start=1):
        with Image.open(image_path) as image:
            gray = image.convert("L")
            width, height = gray.size
            dimensions.add((width, height))
            pixels = gray.load()
            edge_dark = 0
            for x in range(width):
                for y in (0, 1, height - 2, height - 1):
                    edge_dark += pixels[x, y] < 225
            for y in range(2, height - 2):
                for x in (0, 1, width - 2, width - 1):
                    edge_dark += pixels[x, y] < 225
            if edge_dark:
                edge_hits.append(page_number)

            dark_pixels = sum(value < 242 for value in gray.get_flattened_data())
            dark_ratio = dark_pixels / (width * height)
            if page_number > 1 and dark_ratio < 0.0015:
                sparse_pages.append(page_number)

    return RenderResult(
        name=pdf.name,
        pages=len(pages),
        dimensions=dimensions,
        edge_hits=edge_hits,
        sparse_pages=sparse_pages,
    )


def _write_report_section(lines: list[str]) -> None:
    base = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    marker = f"\n{SECTION_MARKER}\n"
    if marker in base:
        base = base.split(marker, 1)[0].rstrip() + "\n"
    REPORT.write_text(base.rstrip() + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    pdfs = sorted(DIST.glob("*.pdf"))
    if len(pdfs) != 4:
        print(f"Expected four PDFs, found {len(pdfs)}.", file=sys.stderr)
        return 1
    if shutil.which("pdftoppm") is None:
        print("pdftoppm is required for rendered-page QA.", file=sys.stderr)
        return 1

    RENDER_ROOT.mkdir(parents=True, exist_ok=True)
    results = [_inspect(pdf) for pdf in pdfs]
    errors: list[str] = []
    lines = [SECTION_MARKER, ""]
    for result in results:
        if result.edge_hits:
            errors.append(f"{result.name}: dark pixels touch outer edge on pages {result.edge_hits}")
        if result.sparse_pages:
            errors.append(f"{result.name}: suspiciously sparse pages {result.sparse_pages}")
        lines.extend(
            [
                f"### {result.name}",
                "",
                f"- Rendered pages: {result.pages}",
                f"- Pixel dimensions: `{sorted(result.dimensions)}`",
                f"- Edge-collision pages: {result.edge_hits or 'None'}",
                f"- Suspiciously sparse pages: {result.sparse_pages or 'None'}",
                "",
            ]
        )
    lines.extend(["### Render errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    _write_report_section(lines)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Rendered and checked {sum(result.pages for result in results)} pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
