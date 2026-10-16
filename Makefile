PY      ?= .venv/bin/python
APP     ?=
COMPANY ?=
ROLE    ?=

.PHONY: help setup test cv cv-example cv-app new-app clean

help:  ## list targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-12s %s\n", $$1, $$2}'

setup:  ## create venv, install deps and Chromium
	python3 -m venv .venv
	$(PY) -m pip install -q --upgrade pip
	$(PY) -m pip install -q -r requirements.txt
	$(PY) -m playwright install chromium

test:  ## run test suite
	$(PY) -m pytest -q

cv:  ## render master CV → cv/out/master.{html,pdf}
	$(PY) tools/build_cv.py cv/data/master.yaml -o cv/out/master --pdf

cv-example:  ## render the fictional example CVs (mid, first-job, veteran)
	@for f in cv/data/example*.yaml; do $(PY) tools/build_cv.py $$f -o cv/out/$$(basename $$f .yaml) --pdf; done

li-zip:  ## import LinkedIn data export: make li-zip ZIP=profile/sources/<export>.zip
	@test -n "$(ZIP)" || (echo "usage: make li-zip ZIP=path/to/export.zip"; exit 2)
	$(PY) tools/linkedin_import.py zip "$(ZIP)"

li-api:  ## import via LinkedIn Member Data Portability API (EEA/CH; needs LINKEDIN_DMA_TOKEN)
	$(PY) tools/linkedin_import.py api

li-post:  ## dry-run a post: make li-post POST=campaign/posts/<file>.md
	@test -n "$(POST)" || (echo "usage: make li-post POST=campaign/posts/<file>.md"; exit 2)
	$(PY) tools/linkedin_post.py "$(POST)"

cv-app:  ## render an application CV: make cv-app APP=applications/<dir>
	@test -n "$(APP)" || (echo "usage: make cv-app APP=applications/<dir>"; exit 2)
	$(PY) tools/build_cv.py $(APP)/cv.yaml -o $(APP)/out/cv --pdf

new-app:  ## scaffold: make new-app COMPANY="Acme" ROLE="Project Manager"
	@test -n "$(COMPANY)" -a -n "$(ROLE)" || (echo 'usage: make new-app COMPANY="…" ROLE="…"'; exit 2)
	$(PY) tools/new_application.py --company "$(COMPANY)" --role "$(ROLE)"

clean:  ## remove rendered output
	rm -rf cv/out applications/*/out
