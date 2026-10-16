#!/usr/bin/env python3
"""Import your own LinkedIn profile into a DRAFT CV YAML.

Two sources, one normaliser:

  zip  — LinkedIn's "Get a copy of your data" archive (works for everyone).
         LinkedIn → Settings → Data privacy → Get a copy of your data.
  api  — Member Data Portability API (EEA + Switzerland members only, self-serve).
         GET https://api.linkedin.com/rest/memberSnapshotData?q=criteria&domain=<D>
         Header Linkedin-Version: 202312. Token from env LINKEDIN_DMA_TOKEN
         (scope r_dma_portability_self_serve, generated in the LinkedIn developer portal).

Both return flat records keyed by human-readable column names ("First Name",
"Company Name", "Started On", …), so the same normaliser serves both.

Output is a DRAFT. The profile-intake skill must confirm every line with the owner
before anything reaches profile/profile.md or cv/data/master.yaml.

Usage:
    python tools/linkedin_import.py zip ~/Downloads/Basic_LinkedInDataExport.zip
    LINKEDIN_DMA_TOKEN=… python tools/linkedin_import.py api
    python tools/linkedin_import.py snapshot profile/sources/linkedin-snapshot.json
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "profile" / "sources"

# domain → (export CSV basename, a column that identifies the header row)
DOMAINS: dict[str, tuple[str, str]] = {
    "PROFILE": ("Profile.csv", "First Name"),
    "POSITIONS": ("Positions.csv", "Company Name"),
    "EDUCATION": ("Education.csv", "School Name"),
    "SKILLS": ("Skills.csv", "Name"),
    "LANGUAGES": ("Languages.csv", "Name"),
    "CERTIFICATIONS": ("Certifications.csv", "Name"),
    "PROJECTS": ("Projects.csv", "Title"),
    "VOLUNTEERING_EXPERIENCES": ("Volunteering.csv", "Company Name"),
}

# Fields that are never imported, even if present (privacy by default).
DROPPED_FIELDS = {"birthdate", "address", "zipcode", "maidenname", "instantmessengers",
                  "licensenumber", "twitterhandles"}

API_URL = "https://api.linkedin.com/rest/memberSnapshotData"
API_VERSION = "202312"   # the only version this endpoint accepts (per Microsoft Learn docs)

_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}


# ── helpers ─────────────────────────────────────────────────────────────────

def _norm(key: str) -> str:
    return re.sub(r"[^a-z0-9]", "", key.lower())


def pick(record: dict, *names: str) -> str:
    """Case/space-insensitive field lookup; returns '' when absent."""
    idx = {_norm(k): v for k, v in record.items()}
    for n in names:
        v = idx.get(_norm(n))
        if v not in (None, ""):
            return str(v).strip()
    return ""


def parse_date(value: str) -> str | None:
    """'Mar 2021'→'2021-03', 'March 2021'→'2021-03', '2021'→'2021', '03/2021'→'2021-03',
    '2021-03-15'→'2021-03'. Empty → None (meaning 'present' for end dates)."""
    s = (value or "").strip()
    if not s or s.lower() in {"present", "now"}:
        return None
    m = re.fullmatch(r"([A-Za-z]{3,})\.?\s+(\d{4})", s)
    if m and m.group(1)[:3].lower() in _MONTHS:
        return f"{m.group(2)}-{_MONTHS[m.group(1)[:3].lower()]:02d}"
    m = re.fullmatch(r"(\d{1,2})/(\d{4})", s)
    if m:
        return f"{m.group(2)}-{int(m.group(1)):02d}"
    m = re.fullmatch(r"(\d{4})-(\d{1,2})(?:-\d{1,2})?", s)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}"
    m = re.fullmatch(r"(\d{4})", s)
    if m:
        return m.group(1)
    return s


def split_bullets(text: str) -> list[str]:
    """Turn a LinkedIn description into candidate bullets."""
    if not text:
        return []
    lines = re.split(r"\r?\n|\s•\s|^•\s", text)
    out = []
    for ln in lines:
        ln = re.sub(r"^\s*[-•*–·]\s*", "", ln).strip()
        if ln:
            out.append(ln)
    return out


def _humanise_level(level: str) -> str:
    return level.replace("_", " ").strip().capitalize() if level else ""


# ── normaliser ──────────────────────────────────────────────────────────────

def normalise(data: dict[str, list[dict]], source: str) -> dict[str, Any]:
    """Map raw domain records to the CV YAML schema (draft)."""
    prof = (data.get("PROFILE") or [{}])[0]
    name = " ".join(p for p in (pick(prof, "First Name"), pick(prof, "Last Name")) if p)
    websites = pick(prof, "Websites")
    m = re.search(r"(?:https?://)?(?:[\w-]+\.)*linkedin\.com/[^\s,\[\]]+", websites)
    linkedin = m.group(0) if m else ""

    experience = []
    for r in data.get("POSITIONS", []):
        experience.append({
            "title": pick(r, "Title"),
            "company": pick(r, "Company Name", "Company"),
            "location": pick(r, "Location"),
            "start": parse_date(pick(r, "Started On", "Start Date")),
            "end": parse_date(pick(r, "Finished On", "End Date")) or "present",
            "bullets": split_bullets(pick(r, "Description")),
        })

    education = []
    for r in data.get("EDUCATION", []):
        details = "; ".join(x for x in (pick(r, "Notes"), pick(r, "Activities")) if x)
        education.append({
            "degree": pick(r, "Degree Name", "Degree") or "(degree?)",
            "institution": pick(r, "School Name", "School"),
            "start": parse_date(pick(r, "Start Date", "Started On")),
            "end": parse_date(pick(r, "End Date", "Finished On")),
            "details": details,
        })

    skills = [pick(r, "Name", "Skill") for r in data.get("SKILLS", []) if pick(r, "Name", "Skill")]

    languages = [{"name": pick(r, "Name", "Language"),
                  "level": _humanise_level(pick(r, "Proficiency"))}
                 for r in data.get("LANGUAGES", []) if pick(r, "Name", "Language")]

    certifications = []
    for r in data.get("CERTIFICATIONS", []):
        started = parse_date(pick(r, "Started On", "Start Date")) or ""
        certifications.append({"name": pick(r, "Name"), "issuer": pick(r, "Authority", "Issuer"),
                               "year": started[:4]})

    projects = [{"title": pick(r, "Title"),
                 "start": parse_date(pick(r, "Started On")),
                 "end": parse_date(pick(r, "Finished On")),
                 "url": pick(r, "Url"),
                 "bullets": split_bullets(pick(r, "Description"))}
                for r in data.get("PROJECTS", []) if pick(r, "Title")]

    volunteering = [{"title": pick(r, "Role"),
                     "company": pick(r, "Company Name", "Organization"),
                     "start": parse_date(pick(r, "Started On")),
                     "end": parse_date(pick(r, "Finished On")) or "present",
                     "context": pick(r, "Cause"),
                     "bullets": split_bullets(pick(r, "Description"))}
                    for r in data.get("VOLUNTEERING_EXPERIENCES", []) if pick(r, "Role")]

    draft: dict[str, Any] = {
        "_draft": {
            "source": source,
            "generated": dt.date.today().isoformat(),
            "warning": "UNVERIFIED import. Confirm every line with the owner (profile-intake) "
                       "before copying anything into profile.md or master.yaml.",
            "counts": {d: len(data.get(d, [])) for d in DOMAINS},
        },
        "lang": "en",
        "person": {
            "name": name or "(name?)",
            "headline": pick(prof, "Headline") or "(headline?)",
            "location": pick(prof, "Geo Location", "Location"),
            "linkedin": linkedin,
        },
        "summary": pick(prof, "Summary"),
        "experience": experience,
    }
    for key, val in (("education", education), ("projects", projects),
                     ("volunteering", volunteering), ("languages", languages),
                     ("certifications", certifications)):
        if val:
            draft[key] = val
    if skills:
        draft["skills"] = [{"group": "LinkedIn skills (prune!)", "items": skills}]
    return draft


def _strip_private(records: list[dict]) -> list[dict]:
    return [{k: v for k, v in r.items() if _norm(k) not in DROPPED_FIELDS} for r in records]


# ── source: export ZIP ──────────────────────────────────────────────────────

def _read_csv(text: str, header_key: str) -> list[dict]:
    rows = list(csv.reader(io.StringIO(text)))
    for i, row in enumerate(rows):  # some exports prepend "Notes:" lines before the header
        if _norm(header_key) in {_norm(c) for c in row}:
            header = row
            return [dict(zip(header, r)) for r in rows[i + 1:] if any(c.strip() for c in r)]
    return []


def load_zip(path: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    with zipfile.ZipFile(path) as zf:
        by_name = {Path(n).name.lower(): n for n in zf.namelist()}
        for domain, (fname, header_key) in DOMAINS.items():
            member = by_name.get(fname.lower())
            if member:
                text = zf.read(member).decode("utf-8-sig", errors="replace")
                out[domain] = _strip_private(_read_csv(text, header_key))
    return out


# ── source: Member Data Portability API ─────────────────────────────────────

Opener = Callable[..., Any]


def fetch_domain(domain: str, token: str, opener: Opener = urllib.request.urlopen,
                 max_pages: int = 100) -> list[dict]:
    """Fetch one snapshot domain, following paging 'next' links until exhausted.
    Per the docs, the end is signalled by an error 'No data found for this memberId'."""
    url = f"{API_URL}?q=criteria&domain={domain}"
    records: list[dict] = []
    for _ in range(max_pages):
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Linkedin-Version": API_VERSION,
        })
        try:
            with opener(req, timeout=30) as resp:
                body = json.load(resp)
        except urllib.error.HTTPError as exc:
            msg = exc.read().decode("utf-8", "replace") if exc.fp else ""
            if exc.code == 404 or "No data found" in msg:
                break
            raise RuntimeError(f"{domain}: HTTP {exc.code} {msg[:200]}") from exc
        page = [rec for el in body.get("elements", []) for rec in el.get("snapshotData", [])]
        if not page:
            break
        records.extend(page)
        nxt = next((l["href"] for l in body.get("paging", {}).get("links", [])
                    if l.get("rel") == "next" and l.get("href")), None)
        if not nxt:
            break
        url = nxt if nxt.startswith("http") else f"https://api.linkedin.com{nxt}"
    return _strip_private(records)


def load_api(token: str, opener: Opener = urllib.request.urlopen,
             domains: Iterable[str] = DOMAINS) -> dict[str, list[dict]]:
    return {d: fetch_domain(d, token, opener) for d in domains}


# ── CLI ─────────────────────────────────────────────────────────────────────

def write_draft(draft: dict, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(draft, allow_unicode=True, sort_keys=False, width=100),
                   encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    z = sub.add_parser("zip", help="import a LinkedIn data-export ZIP")
    z.add_argument("path", type=Path)
    a = sub.add_parser("api", help="fetch via Member Data Portability API (EEA/CH)")
    a.add_argument("--cache", type=Path, default=SOURCES / "linkedin-snapshot.json")
    s = sub.add_parser("snapshot", help="re-normalise a cached API snapshot JSON")
    s.add_argument("path", type=Path)
    for p in (z, a, s):
        p.add_argument("-o", "--out", type=Path, default=SOURCES / "linkedin-draft.yaml")
    args = ap.parse_args(argv)

    if args.cmd == "zip":
        if not args.path.exists():
            print(f"error: {args.path} not found", file=sys.stderr)
            return 2
        data, source = load_zip(args.path), f"export-zip:{args.path.name}"
    elif args.cmd == "api":
        token = os.environ.get("LINKEDIN_DMA_TOKEN", "").strip()
        if not token:
            print("error: set LINKEDIN_DMA_TOKEN (see docs/linkedin.md)", file=sys.stderr)
            return 2
        data, source = load_api(token), "dma-api"
        args.cache.parent.mkdir(parents=True, exist_ok=True)
        args.cache.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"cache → {args.cache}")
    else:
        data, source = json.loads(args.path.read_text(encoding="utf-8")), f"snapshot:{args.path.name}"

    draft = normalise(data, source)
    write_draft(draft, args.out)
    counts = ", ".join(f"{k.lower()}={v}" for k, v in draft["_draft"]["counts"].items() if v)
    print(f"draft → {args.out}  ({counts or 'no records found'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
