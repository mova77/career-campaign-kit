import copy
import datetime as dt
import shutil
from pathlib import Path

import pytest
import yaml

import build_cv as b

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "cv" / "data" / "example.yaml"


@pytest.fixture
def cv():
    return yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))


# ── validation ──

def test_example_is_valid(cv):
    assert b.validate(cv) == []


@pytest.mark.parametrize("mutate, expected", [
    (lambda c: c.pop("lang"), "lang"),
    (lambda c: c["person"].update(name=""), "person.name"),
    (lambda c: c.update(experience=[], education=[]), "experience/education/projects"),
    (lambda c: c.update(stage="intern"), "stage"),
    (lambda c: c.update(sections=["summary", "hobbies"]), "sections"),
    (lambda c: c.update(projects=[{"role": "x"}]), "projects[0].title"),
    (lambda c: c.update(earlier_career=[{"company": "x"}]), "earlier_career[0].title"),
    (lambda c: c.update(highlights=["ok", ""]), "highlights"),
    (lambda c: c["experience"][0].pop("company"), "experience[0].company"),
    (lambda c: c["experience"][0].pop("start"), "experience[0].start"),
    (lambda c: c["experience"][0].update(bullets=["ok", ""]), "experience[0].bullets"),
    (lambda c: c["education"][0].pop("institution"), "education[0].institution"),
    (lambda c: c["skills"][0].update(items=[]), "skills[0]"),
])
def test_validation_catches(cv, mutate, expected):
    mutate(cv)
    errors = b.validate(cv)
    assert any(e.startswith(expected) for e in errors), errors


def test_validate_rejects_non_mapping():
    assert b.validate(["not", "a", "dict"]) == ["top level must be a mapping"]


# ── formatting ──

@pytest.mark.parametrize("value, out", [
    ("2021-03", "03/2021"),
    ("2021-3", "03/2021"),
    (2015, "2015"),
    (dt.date(2020, 7, 1), "07/2020"),
    ("present", "obecnie"),
    (None, "obecnie"),
    ("", "obecnie"),
])
def test_format_ym(value, out):
    assert b.format_ym(value, "obecnie") == out


# ── rendering ──

def test_render_contains_core_content(cv):
    cv["labels"] = {**b.DEFAULT_LABELS, **cv["labels"]}
    cv["theme"] = {**b.DEFAULT_THEME, **cv["theme"]}
    html = b.render_html(cv)
    assert "<h1>Alex Example</h1>" in html
    assert "Northwind Bank" in html
    assert "03/2021 – present" in html
    assert 'href="mailto:alex.example@example.com"' in html
    assert 'href="https://linkedin.com/in/alex-example"' in html


def test_render_escapes_html(cv):
    cv["experience"][0]["bullets"] = ["<script>alert(1)</script> & more"]
    cv["labels"] = dict(b.DEFAULT_LABELS)
    cv["theme"] = dict(b.DEFAULT_THEME)
    html = b.render_html(cv)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_labels_localise_and_default(tmp_path, cv):
    cv["lang"] = "pl"
    cv["labels"] = {"experience": "Doświadczenie", "present": "obecnie"}
    src = tmp_path / "cv.yaml"
    src.write_text(yaml.safe_dump(cv, allow_unicode=True), encoding="utf-8")
    html = b.render_html(b.load_cv(src))
    assert "Doświadczenie" in html
    assert "obecnie" in html
    assert ">Education<" in html          # untranslated label falls back to English
    assert '<html lang="pl">' in html


def test_minimal_cv_renders(tmp_path):
    minimal = {"lang": "en",
               "person": {"name": "Min", "headline": "H"},
               "experience": [{"title": "T", "company": "C", "start": 2020}]}
    src = tmp_path / "min.yaml"
    src.write_text(yaml.safe_dump(minimal), encoding="utf-8")
    html = b.render_html(b.load_cv(src))
    assert "<h1>Min</h1>" in html


def test_cli_reports_validation_error(tmp_path, capsys):
    bad = tmp_path / "bad.yaml"
    bad.write_text("lang: en\n", encoding="utf-8")
    assert b.main([str(bad), "-o", str(tmp_path / "x")]) == 1
    assert "person: required" in capsys.readouterr().err


def test_cli_missing_master_hint(tmp_path, capsys):
    assert b.main([str(tmp_path / "master.yaml")]) == 2
    assert "profile-intake" in capsys.readouterr().err


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch().close()
        return True
    except Exception:
        return False


STAGE_EXAMPLES = sorted((ROOT / "cv" / "data").glob("example*.yaml"))


def _order_of(html: str, *markers: str) -> list[int]:
    return [html.index(m) for m in markers]


def test_first_job_puts_education_before_experience():
    html = b.render_html(b.load_cv(ROOT / "cv" / "data" / "example-first-job.yaml"))
    edu, proj, exp = _order_of(html, 'class="education"', 'class="projects"', 'class="experience"')
    assert edu < proj < exp
    assert "Volunteering" in html


def test_veteran_has_highlights_and_compressed_early_career():
    html = b.render_html(b.load_cv(ROOT / "cv" / "data" / "example-veteran.yaml"))
    hl, exp, early = _order_of(html, 'class="highlights"', 'class="experience"', 'class="earlier"')
    assert hl < exp < early
    assert "Earlier career" in html and "2000" in html
    # education without dates renders no stray "present"
    edu_block = html[html.index('class="education"'):html.index('class="skills"')]
    assert "present" not in edu_block


def test_sections_override(cv):
    cv["sections"] = ["skills", "experience"]
    html = b.render_html(cv)
    assert html.index('class="skills"') < html.index('class="experience"')
    assert 'class="education"' not in html


def test_education_only_cv_is_valid(tmp_path):
    src = tmp_path / "e.yaml"
    src.write_text(yaml.safe_dump({
        "lang": "en", "stage": "first-job", "person": {"name": "E", "headline": "Student"},
        "education": [{"degree": "BSc", "institution": "Uni", "end": 2026}]}), encoding="utf-8")
    assert "BSc" in b.render_html(b.load_cv(src))


@pytest.mark.skipif(not _chromium_available(), reason="Chromium not installed for Playwright")
@pytest.mark.parametrize("src", STAGE_EXAMPLES, ids=lambda p: p.stem)
def test_pdf_examples_within_stage_budget(tmp_path, src):
    html, pdf, budget = b.build(src, tmp_path / src.stem, pdf=True)
    assert pdf.exists() and pdf.stat().st_size > 5_000
    pages = b.pdf_page_count(pdf)
    if pages is not None:
        assert 1 <= pages <= budget
