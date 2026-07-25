from __future__ import annotations

import hashlib

from PIL import Image
from pypdf import PdfReader, PdfWriter

from scripts import render_validate, validate_pdfs


def test_checksum_manifest_requires_exact_release_set(tmp_path, monkeypatch):
    checksum_path = tmp_path / "SHA256SUMS"
    digest = "a" * 64
    checksum_path.write_text(f"{digest}  dist/example.pdf\n", encoding="utf-8")
    monkeypatch.setattr(validate_pdfs, "CHECKSUMS", checksum_path)
    monkeypatch.setattr(
        validate_pdfs,
        "OUTPUTS",
        {("zh", "exercises"): "example.pdf"},
    )

    entries, errors = validate_pdfs._checksum_entries()

    assert entries == {"example.pdf": digest}
    assert errors == []


def test_security_audit_rejects_embedded_javascript(tmp_path):
    pdf_path = tmp_path / "javascript.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.add_js("app.alert('unsafe')")
    with pdf_path.open("wb") as stream:
        writer.write(stream)

    issues = validate_pdfs._security_issues(PdfReader(pdf_path))

    assert any("/JavaScript" in issue for issue in issues)


def test_contact_sheet_covers_every_rendered_page(tmp_path):
    page_paths = []
    for number in range(1, 22):
        page_path = tmp_path / f"page-{number:03d}.png"
        Image.new("RGB", (80, 60), (number, number, number)).save(page_path)
        page_paths.append(page_path)

    count = render_validate._make_contact_sheets(tmp_path, page_paths)

    assert count == 2
    assert len(list(tmp_path.glob("contact-sheet-*.png"))) == 2


def test_sha256_helper_reads_binary_content(tmp_path):
    path = tmp_path / "artifact.pdf"
    path.write_bytes(b"release bytes")

    assert validate_pdfs._sha256(path) == hashlib.sha256(b"release bytes").hexdigest()
