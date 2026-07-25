from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import sys

from PIL import Image, ImageDraw
import pypdfium2 as pdfium


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RENDER_ROOT = ROOT / "work" / "rendered_final"
REPORT = ROOT / "reports" / "pdf_validation.md"
SECTION_MARKER = "## Full-page PDFium render and pixel QA"
RENDER_SCALE = 1.15
CONTACT_COLUMNS = 4
CONTACT_ROWS = 5
CONTACT_CELL = (250, 210)
CONTACT_THUMBNAIL = (230, 178)


@dataclass(frozen=True)
class RenderResult:
    name: str
    pages: int
    dimensions: set[tuple[int, int]]
    edge_hits: list[int]
    sparse_pages: list[int]
    contact_sheets: int


def _dark_ratio(image: Image.Image, threshold: int = 242) -> float:
    gray = image.convert("L")
    histogram = gray.histogram()
    return sum(histogram[:threshold]) / (gray.width * gray.height)


def _edge_has_ink(image: Image.Image, threshold: int = 225) -> bool:
    gray = image.convert("L")
    width, height = gray.size
    borders = (
        gray.crop((0, 0, width, 2)),
        gray.crop((0, height - 2, width, height)),
        gray.crop((0, 2, 2, height - 2)),
        gray.crop((width - 2, 2, width, height - 2)),
    )
    return any(border.getextrema()[0] < threshold for border in borders)


def _make_contact_sheets(output_dir: Path, page_paths: list[Path]) -> int:
    per_sheet = CONTACT_COLUMNS * CONTACT_ROWS
    sheet_count = 0
    for offset in range(0, len(page_paths), per_sheet):
        sheet_count += 1
        canvas = Image.new(
            "RGB",
            (CONTACT_COLUMNS * CONTACT_CELL[0], CONTACT_ROWS * CONTACT_CELL[1]),
            "white",
        )
        draw = ImageDraw.Draw(canvas)
        for slot, page_path in enumerate(page_paths[offset : offset + per_sheet]):
            with Image.open(page_path) as source:
                thumbnail = source.convert("RGB")
                thumbnail.thumbnail(CONTACT_THUMBNAIL, Image.Resampling.LANCZOS)
            column = slot % CONTACT_COLUMNS
            row = slot // CONTACT_COLUMNS
            cell_x = column * CONTACT_CELL[0]
            cell_y = row * CONTACT_CELL[1]
            x = cell_x + (CONTACT_CELL[0] - thumbnail.width) // 2
            y = cell_y + 18 + (CONTACT_THUMBNAIL[1] - thumbnail.height) // 2
            canvas.paste(thumbnail, (x, y))
            draw.rectangle(
                (x - 1, y - 1, x + thumbnail.width, y + thumbnail.height),
                outline=(185, 190, 200),
                width=1,
            )
            draw.text((cell_x + 8, cell_y + 4), page_path.stem, fill=(45, 50, 60))
        canvas.save(output_dir / f"contact-sheet-{sheet_count:03d}.png", optimize=True)
    return sheet_count


def _inspect(pdf_path: Path) -> RenderResult:
    output_dir = RENDER_ROOT / pdf_path.stem
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    document = pdfium.PdfDocument(pdf_path)
    edge_hits: list[int] = []
    sparse_pages: list[int] = []
    dimensions: set[tuple[int, int]] = set()
    page_paths: list[Path] = []
    pages_rendered = 0
    for zero_index, page in enumerate(document):
        page_number = zero_index + 1
        pages_rendered = page_number
        image = page.render(scale=RENDER_SCALE).to_pil().convert("RGB")
        dimensions.add(image.size)
        page_path = output_dir / f"page-{page_number:03d}.png"
        image.save(page_path, optimize=True)
        page_paths.append(page_path)
        if page_number > 1 and _edge_has_ink(image):
            edge_hits.append(page_number)
        if page_number > 1 and _dark_ratio(image) < 0.0015:
            sparse_pages.append(page_number)
        page.close()
    document.close()
    contact_sheets = _make_contact_sheets(output_dir, page_paths)
    return RenderResult(
        name=pdf_path.name,
        pages=pages_rendered,
        dimensions=dimensions,
        edge_hits=edge_hits,
        sparse_pages=sparse_pages,
        contact_sheets=contact_sheets,
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

    RENDER_ROOT.mkdir(parents=True, exist_ok=True)
    results = [_inspect(pdf) for pdf in pdfs]
    errors: list[str] = []
    lines = [SECTION_MARKER, ""]
    for result in results:
        if result.edge_hits:
            errors.append(f"{result.name}: ink touches the outer edge on pages {result.edge_hits}")
        if result.sparse_pages:
            errors.append(f"{result.name}: suspiciously sparse pages {result.sparse_pages}")
        lines.extend(
            [
                f"### {result.name}",
                "",
                f"- PDFium-rendered pages: {result.pages}",
                f"- Pixel dimensions: `{sorted(result.dimensions)}`",
                f"- Edge-collision pages (cover excluded): {result.edge_hits or 'None'}",
                f"- Suspiciously sparse pages: {result.sparse_pages or 'None'}",
                f"- Contact sheets for visual review: {result.contact_sheets}",
                "",
            ]
        )
    lines.extend(["### Render errors", ""])
    lines.extend([f"- {error}" for error in errors] or ["- None"])
    _write_report_section(lines)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Rendered and checked {sum(result.pages for result in results)} pages with PDFium.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
