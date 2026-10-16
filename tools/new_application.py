#!/usr/bin/env python3
"""Scaffold an application folder from applications/_template.

Usage:
    python tools/new_application.py --company "Acme Corp" --role "Project Manager" [--date 2026-11-03]

Creates applications/<date>-<company-slug>-<role-slug>/ with the template files
(placeholders filled) and a copy of cv/data/master.yaml as cv.yaml, if it exists.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Characters NFKD does not decompose to ASCII (Polish ł, German ß, Nordic ø, …).
_TRANSLIT = str.maketrans({"ł": "l", "Ł": "L", "ß": "ss", "ø": "o", "Ø": "O",
                           "đ": "d", "Đ": "D", "æ": "ae", "Æ": "AE", "œ": "oe"})


def slugify(text: str, max_len: int = 40) -> str:
    text = text.translate(_TRANSLIT)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:max_len].rstrip("-") or "x"


def scaffold(company: str, role: str, date: dt.date, root: Path = ROOT) -> Path:
    template = root / "applications" / "_template"
    target = root / "applications" / f"{date.isoformat()}-{slugify(company)}-{slugify(role)}"
    if target.exists():
        raise FileExistsError(f"{target} already exists")
    shutil.copytree(template, target)

    repl = {"{{COMPANY}}": company, "{{ROLE}}": role, "{{DATE}}": date.isoformat()}
    for f in target.rglob("*.md"):
        txt = f.read_text(encoding="utf-8")
        for k, v in repl.items():
            txt = txt.replace(k, v)
        f.write_text(txt, encoding="utf-8")

    master = root / "cv" / "data" / "master.yaml"
    if master.exists():
        shutil.copy(master, target / "cv.yaml")
    return target


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--company", required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--date", type=dt.date.fromisoformat, default=dt.date.today())
    args = ap.parse_args(argv)
    try:
        path = scaffold(args.company, args.role, args.date)
    except FileExistsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
