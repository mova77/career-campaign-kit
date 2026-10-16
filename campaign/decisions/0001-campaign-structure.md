# ADR-0001 — Run the job search as a repository-backed campaign

- **Status:** accepted
- **Date:** <set at first session>

## Context
Job searches drift: facts get re-explained every chat, CV versions multiply, recruiter
threads are forgotten, and decisions get re-litigated. Chat memory alone is lossy.

## Decision
- The repository is the single source of truth: facts in `profile/`, state in `campaign/`,
  one folder per application.
- Claude reads `CLAUDE.md` + `campaign/STATE.md` every session and writes state back at the end.
- Opportunities are triaged with a weighted rubric before any tailoring effort.
- Lasting decisions are recorded as ADRs in this folder (template: `0000-template.md`).

## Consequences
- + Continuity across sessions, devices and Claude surfaces.
- + Every CV claim is traceable to a confirmed fact.
- − Requires the discipline of a short state update at the end of each session (the agent does it).
