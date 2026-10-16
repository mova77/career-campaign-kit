#!/usr/bin/env python3
"""Render a CV from YAML to a single-file HTML page and (optionally) an A4 PDF.

Usage:
    python tools/build_cv.py cv/data/master.yaml -o cv/out/master --pdf
    python tools/build_cv.py applications/<dir>/cv.yaml -o applications/<dir>/out/cv --pdf

Pipeline:  YAML ──validate──▶ dict ──Jinja2──▶ HTML (CSS inlined) ──Chromium print──▶ PDF
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "cv" / "templates"

DEFAULT_LABELS = {
    "summary": "Profile",
    "experience": "Experience",
    "education": "Education",
    "skills": "Skills",
    "languages": "Languages",
    "certifications": "Certifications",
    "projects": "Projects",
    "volunteering": "Volunteering",
    "highlights": "Selected achievements",
    "earlier_career": "Earlier career",
    "present": "present",
}
DEFAULT_THEME = {"accent": "#1F5F8B"}

SECTION_KEYS = {"summary", "highlights", "experience", "earlier_career", "projects",
                "education", "volunteering", "skills", "extras"}

# Career stage → (default section order, page budget). Override order with `sections:`.
STAGES: dict[str, tuple[list[str], int]] = {
    "first-job": (["summary", "education", "projects", "experience", "volunteering", "skills", "extras"], 1),
    "early":     (["summary", "experience", "projects", "education", "skills", "volunteering", "extras"], 1),
    "mid":       (["summary", "experience", "projects", "education", "skills", "volunteering", "extras"], 2),
    "senior":    (["summary", "highlights", "experience", "earlier_career", "education", "skills", "extras"], 2),
    "executive": (["summary", "highlights", "experience", "earlier_career", "education", "extras"], 2),
    "returner":  (["summary", "experience", "projects", "education", "skills", "volunteering", "extras"], 2),
    "career-changer": (["summary", "highlights", "projects", "experience", "education", "skills", "extras"], 2),
}
DEFAULT_STAGE = "mid"


class CVValidationError(ValueError):
    """Raised when CV data does not satisfy the schema."""

    def __init__(self, errors: list[str]):
        super().__init__("Invalid CV data:\n  - " + "\n  - ".join(errors))
        self.errors = errors


# ── validation ──────────────────────────────────────────────────────────────

def _is_nonempty_str(v: Any) -> bool:
    return isinstance(v, str) and v.strip() != ""


def validate(cv: Any) -> list[str]:
    """Return a list of human-readable schema violations (empty list = valid)."""
    errors: list[str] = []
    if not isinstance(cv, dict):
        return ["top level must be a mapping"]

    if not _is_nonempty_str(cv.get("lang")):
        errors.append("lang: required (e.g. 'en', 'pl', 'it')")

    person = cv.get("person")
    if not isinstance(person, dict):
        errors.append("person: required mapping")
    else:
        for key in ("name", "headline"):
            if not _is_nonempty_str(person.get(key)):
                errors.append(f"person.{key}: required non-empty string")

    stage = cv.get("stage", DEFAULT_STAGE)
    if stage not in STAGES:
        errors.append(f"stage: must be one of {', '.join(STAGES)}")
    sections = cv.get("sections")
    if sections is not None:
        if not isinstance(sections, list) or not sections:
            errors.append("sections: must be a non-empty list")
        else:
            unknown = [s for s in sections if s not in SECTION_KEYS]
            if unknown:
                errors.append(f"sections: unknown {unknown}; allowed {sorted(SECTION_KEYS)}")

    # A first-job CV may have no employment yet — but it must have *something* substantive.
    if not any(isinstance(cv.get(k), list) and cv.get(k) for k in ("experience", "education", "projects")):
        errors.append("experience/education/projects: at least one must be a non-empty list")

    for section in ("experience", "projects", "volunteering"):
        items = cv.get(section)
        if items is None:
            continue
        if not isinstance(items, list):
            errors.append(f"{section}: must be a list")
            continue
        title_req = ("title",) if section == "projects" else ("title", "company")
        for i, job in enumerate(items):
            if not isinstance(job, dict):
                errors.append(f"{section}[{i}]: must be a mapping")
                continue
            for key in title_req:
                if not _is_nonempty_str(job.get(key)):
                    errors.append(f"{section}[{i}].{key}: required")
            if section == "experience" and job.get("start") in (None, ""):
                errors.append(f"experience[{i}].start: required (YYYY-MM or YYYY)")
            bullets = job.get("bullets", [])
            if not isinstance(bullets, list) or not all(_is_nonempty_str(b) for b in bullets):
                errors.append(f"{section}[{i}].bullets: must be a list of non-empty strings")

    for i, e in enumerate(cv.get("earlier_career") or []):
        if not isinstance(e, dict) or not _is_nonempty_str(e.get("title")):
            errors.append(f"earlier_career[{i}].title: required")

    hl = cv.get("highlights")
    if hl is not None and (not isinstance(hl, list) or not all(_is_nonempty_str(h) for h in hl)):
        errors.append("highlights: must be a list of non-empty strings")

    for section, required in (("education", ("degree", "institution")),
                              ("languages", ("name", "level")),
                              ("certifications", ("name",))):
        items = cv.get(section)
        if items is None:
            continue
        if not isinstance(items, list):
            errors.append(f"{section}: must be a list")
            continue
        for i, it in enumerate(items):
            for key in required:
                if not isinstance(it, dict) or it.get(key) in (None, ""):
                    errors.append(f"{section}[{i}].{key}: required")

    skills = cv.get("skills")
    if skills is not None:
        if not isinstance(skills, list):
            errors.append("skills: must be a list of {group, items}")
        else:
            for i, g in enumerate(skills):
                if not isinstance(g, dict) or not _is_nonempty_str(g.get("group")) \
                        or not isinstance(g.get("items"), list) or not g["items"]:
                    errors.append(f"skills[{i}]: needs 'group' and non-empty 'items' list")

    labels = cv.get("labels")
    if labels is not None and not isinstance(labels, dict):
        errors.append("labels: must be a mapping")

    return errors


def load_cv(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        cv = yaml.safe_load(fh)
    errors = validate(cv)
    if errors:
        raise CVValidationError(errors)
    cv["labels"] = {**DEFAULT_LABELS, **(cv.get("labels") or {})}
    cv["theme"] = {**DEFAULT_THEME, **(cv.get("theme") or {})}
    return cv


# ── rendering ───────────────────────────────────────────────────────────────

def format_ym(value: Any, present_label: str = "present") -> str:
    """'2021-03' → '03/2021'; 2015 → '2015'; 'present'/None/'' → label; date → MM/YYYY."""
    if value is None or value == "":
        return present_label
    if isinstance(value, (dt.date, dt.datetime)):
        return f"{value.month:02d}/{value.year}"
    s = str(value).strip()
    if s.lower() in {"present", "now", "current", "obecnie", "oggi", "heute"}:
        return present_label
    parts = s.split("-")
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        return f"{int(parts[1]):02d}/{parts[0]}"
    return s


def _contact_items(person: dict) -> list[dict]:
    items: list[dict] = []
    if person.get("location"):
        items.append({"text": person["location"], "href": None})
    if person.get("email"):
        items.append({"text": person["email"], "href": f"mailto:{person['email']}"})
    if person.get("phone"):
        tel = "".join(ch for ch in str(person["phone"]) if ch.isdigit() or ch == "+")
        items.append({"text": str(person["phone"]), "href": f"tel:{tel}"})
    for key in ("linkedin", "website"):
        url = person.get(key)
        if url:
            href = url if url.startswith("http") else f"https://{url}"
            items.append({"text": url.removeprefix("https://").removeprefix("http://"), "href": href})
    return items


def render_html(cv: dict, templates_dir: Path = TEMPLATES) -> str:
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "j2"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["ym"] = format_ym
    css = (templates_dir / "theme.css").read_text(encoding="utf-8")
    # Optional keys default to falsy so StrictUndefined only catches template typos.
    data = {"summary": "", "highlights": [], "experience": [], "earlier_career": [],
            "projects": [], "education": [], "volunteering": [], "skills": [],
            "languages": [], "certifications": [], "footer": "",
            "labels": dict(DEFAULT_LABELS), "theme": dict(DEFAULT_THEME), **cv}
    for section in ("experience", "projects", "volunteering"):
        for item in data[section]:
            for key in ("company", "role", "location", "context"):
                item.setdefault(key, "")
            item.setdefault("bullets", [])
            item.setdefault("start", None)
            item.setdefault("end", None)
    for e in data["earlier_career"]:
        e.setdefault("company", "")
        e.setdefault("start", None)
        e.setdefault("end", None)
    for e in data["education"]:
        e.setdefault("start", None)
        e.setdefault("end", None)
        e.setdefault("details", "")
        e.setdefault("bullets", [])
    for c in data["certifications"]:
        c.setdefault("issuer", "")
        c.setdefault("year", "")
    return env.get_template("cv.html.j2").render(
        cv=data, L=data["labels"], css=css, contact=_contact_items(data["person"]),
        sections=section_order(data),
    )


def section_order(cv: dict) -> list[str]:
    return cv.get("sections") or STAGES[cv.get("stage", DEFAULT_STAGE)][0]


def page_budget(cv: dict) -> int:
    return STAGES[cv.get("stage", DEFAULT_STAGE)][1]


def render_pdf(html_path: Path, pdf_path: Path) -> None:
    """Print the HTML to A4 PDF with headless Chromium (CSS @page controls margins)."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.resolve().as_uri(), wait_until="load")
        page.emulate_media(media="print")
        page.evaluate("document.fonts ? document.fonts.ready : null")
        page.pdf(path=str(pdf_path), prefer_css_page_size=True, print_background=True)
        browser.close()


def pdf_page_count(pdf_path: Path) -> int | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    return len(PdfReader(str(pdf_path)).pages)


def build(src: Path, out_stem: Path, pdf: bool) -> tuple[Path, Path | None, int]:
    """Returns (html_path, pdf_path or None, page budget for the CV's career stage)."""
    cv = load_cv(src)
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    html_path = out_stem.with_suffix(".html")
    html_path.write_text(render_html(cv), encoding="utf-8")
    pdf_path = None
    if pdf:
        pdf_path = out_stem.with_suffix(".pdf")
        render_pdf(html_path, pdf_path)
    return html_path, pdf_path, page_budget(cv)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path, help="CV YAML file")
    ap.add_argument("-o", "--out", type=Path, help="output path stem (default: cv/out/<src stem>)")
    ap.add_argument("--pdf", action="store_true", help="also render PDF via Chromium")
    args = ap.parse_args(argv)

    if not args.src.exists():
        print(f"error: {args.src} not found", file=sys.stderr)
        if args.src.name == "master.yaml":
            print("hint: run the profile-intake skill first, or try `make cv-example`", file=sys.stderr)
        return 2

    out = args.out or (ROOT / "cv" / "out" / args.src.stem)
    try:
        html_path, pdf_path, budget = build(args.src, out, args.pdf)
    except CVValidationError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(f"HTML → {html_path}")
    if pdf_path:
        pages = pdf_page_count(pdf_path)
        suffix = f" ({pages} page{'s' if pages != 1 else ''})" if pages else ""
        print(f"PDF  → {pdf_path}{suffix}")
        if pages and pages > budget:
            print(f"warning: {pages} pages exceeds the {budget}-page budget for this career stage "
                  "— trim bullets, compress older roles into earlier_career", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
