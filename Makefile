PYTHON ?= python3

.PHONY: all merge validate build render test clean-render

all: merge validate build test

merge:
	$(PYTHON) scripts/merge_corpus.py

validate:
	$(PYTHON) scripts/validate_content.py

build:
	$(PYTHON) scripts/build_pdfs.py
	$(PYTHON) scripts/validate_pdfs.py

render:
	$(PYTHON) scripts/render_validate.py

test:
	$(PYTHON) -m pytest -q

clean-render:
	rm -rf work/rendered
