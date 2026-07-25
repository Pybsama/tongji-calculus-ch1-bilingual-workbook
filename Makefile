PYTHON ?= python3

.PHONY: all release merge migrate validate katex build reproducible checksums pdf-check render test clean-render

all: release

release:
	$(PYTHON) scripts/merge_corpus.py
	$(PYTHON) scripts/migrate_latex.py
	$(PYTHON) scripts/validate_content.py
	$(PYTHON) -m pytest -q
	npm run --silent validate:katex
	$(PYTHON) scripts/build_pdfs.py
	$(PYTHON) scripts/verify_reproducible.py
	$(PYTHON) scripts/update_checksums.py
	$(PYTHON) scripts/validate_pdfs.py
	$(PYTHON) scripts/render_validate.py

merge:
	$(PYTHON) scripts/merge_corpus.py

migrate:
	$(PYTHON) scripts/migrate_latex.py

validate:
	$(PYTHON) scripts/validate_content.py

katex:
	npm run --silent validate:katex

build:
	$(PYTHON) scripts/build_pdfs.py

reproducible:
	$(PYTHON) scripts/verify_reproducible.py

checksums:
	$(PYTHON) scripts/update_checksums.py

pdf-check:
	$(PYTHON) scripts/validate_pdfs.py

render:
	$(PYTHON) scripts/render_validate.py

test:
	$(PYTHON) -m pytest -q

clean-render:
	rm -rf work/rendered
