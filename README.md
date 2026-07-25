# Tongji Calculus Chapter 1 - Bilingual Workbook

[简体中文说明](README.zh-CN.md)

A Goodnotes-ready, bilingual practice set for Chapter 1, **Functions and Limits**, aligned with the scope of the seventh edition of Tongji University's *Advanced Mathematics*.

## Downloads

- [Chinese exercise workbook](dist/同济高数第七版_第一章_习题册_中文.pdf)
- [Chinese detailed solutions](dist/同济高数第七版_第一章_超详细解析_中文.pdf)
- [English exercise workbook](dist/Tongji_Calculus_7e_Chapter_1_Exercises_EN.pdf)
- [English detailed solutions](dist/Tongji_Calculus_7e_Chapter_1_Detailed_Solutions_EN.pdf)
- [SHA-256 checksums](SHA256SUMS)

The checksums verify the committed release PDFs. The build fixes its source
epoch, clears each build directory, and pins the Tectonic bundle so that two
consecutive builds can be checked for byte-for-byte reproducibility.

## What is included

- Exactly 100 questions, from basic to challenge level.
- All ten Chapter 1 sections, including two clearly marked optional questions on uniform continuity.
- Eight formats: single choice, multiple choice, true/false with justification, fill-in, calculation, proof, synthesis/application, and error diagnosis.
- Detailed solutions with knowledge points, method selection, numbered derivations, pitfalls, verification, takeaway, and an extension prompt.
- Explicit LaTeX source for mathematics in questions **and** solutions. Every formula segment is first parsed strictly by pinned KaTeX 0.17.0, then compiled into the PDFs by XeTeX with STIX Two Math; the migration audit rejects Unicode shortcuts and slash-style fractions.
- Auditable source lineage: 20 open-text method adaptations, 37 classic-method variants, and 43 original synthesis/diagnosis problems.
- Stable IDs Q001-Q100 across Chinese exercises, Chinese solutions, English exercises, and English solutions.
- Goodnotes-oriented 4:3 layouts: landscape for writing and portrait for reading detailed solutions.

## Scope

The set deliberately uses only Chapter 1 tools. It does **not** use derivatives, L'Hopital's rule, Taylor expansions, or power series.

The lineage labels distinguish open-text method adaptations, classic-method
variants, and original synthesis. They describe method ancestry, not verbatim
provenance. Wording, parameters, and worked solutions are independently
written; commercial textbooks are used only to align chapter scope.

## Study route

1. Complete Foundation, Methods, Synthesis, and Challenge in that order.
2. Attempt each question before opening the solution book.
3. Classify every error as conceptual, algebraic, method-selection, or rigor/communication.
4. Retry wrong items after 48 hours.
5. One week later, sample by knowledge tag rather than by original order.

## Strengths and limitations

The set covers concepts, computation, proofs, parameters, counterexamples, and diagnosis rather than repeating one algebraic pattern. Hard questions remain inside the Chapter 1 boundary.

One hundred questions cannot exhaust every algebraic transformation. Difficulty depends on prior preparation, and a static PDF cannot adapt automatically to a learner's error history. Uniform continuity is starred enrichment in the textbook and may be skipped if it is outside a particular course.

## Build locally

The verified build uses Python 3.12+, Node.js 20+, KaTeX 0.17.0,
exactly Tectonic 0.16.9, and the pinned
`default_bundle_v33`. It uses only bundle-provided open fonts: Fandol, TeX
Gyre Heros, and STIX Two Math; no macOS system font is required. Full-page QA
uses PDFium through `pypdfium2` as a rendering smoke check for dimensions,
nonblank content, edge collisions, and suspiciously sparse pages. Formula
semantics are covered by the per-question audit and strict KaTeX parsing;
representative formula-dense pages are also inspected visually.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
npm ci
# Install exactly Tectonic 0.16.9, or point TECTONIC at that version
python scripts/merge_corpus.py
python scripts/migrate_latex.py  # audit only; must report zero changes
python scripts/validate_content.py
pytest -q
npm run validate:katex  # strictly parses every formula in questions and solutions
python scripts/build_pdfs.py
python scripts/verify_reproducible.py
python scripts/update_checksums.py
python scripts/validate_pdfs.py
python scripts/render_validate.py  # renders and checks every page with PDFium
```

The editable authoring sources are the files in [`content/parts`](content/parts).
`scripts/merge_corpus.py` combines them into the canonical generated corpus
[`content/questions.json`](content/questions.json), from which all four PDFs are built.

## Attribution and status

This is independently authored study material. It is **not** an official publication of Tongji University or Higher Education Press and is not affiliated with either organization. See [SOURCES.md](SOURCES.md) for the per-question lineage policy and public method references, and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the typesetting stack.

Original project content is shared under the terms described in [LICENSE](LICENSE).
The CC BY-NC-SA 4.0 license permits noncommercial sharing and adaptation; its
NonCommercial restriction means this repository is publicly source-available,
not OSI-approved open-source software.
