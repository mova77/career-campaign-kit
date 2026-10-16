---
name: cv-tailor
description: Produce a tailored CV for one application by selecting, re-ordering and re-phrasing verified facts from the master CV, then render it to PDF. Use after an opportunity has been triaged with decision "apply".
---

# CV tailoring

## Preconditions
- Opportunity has a triage score ≥ 65 (or owner overrode) and an application folder.
- `fit-analysis.md` contains the requirement mapping.

## Procedure

1. **Copy** `cv/data/master.yaml` → `<app>/cv.yaml` (if not present).
2. **Language.** Set `lang` and `labels` to the job ad's language (see `cv/data/example.yaml`).
3. **Headline & summary.** Rewrite to the target role in 2–3 lines: who you are, the
   evidence most relevant to *this* JD, what you bring. Only verified facts.
4. **Select & order.**
   - Per role, keep the 3–5 bullets most relevant to the JD's must-haves; drop the rest
     (they stay in master).
   - Put the strongest matching bullet first in each role.
   - Older / less relevant roles: compress to 1–2 bullets or a single line.
5. **Mirror vocabulary — truthfully.** Use the JD's terms where they describe what the
   owner actually did (e.g. JD says "stakeholder management" and the bullet says
   "coordinated with client teams" → rephrase). Never add a skill/tool the owner lacks.
6. **Skills section:** JD-relevant, owner-defended skills first; max ~12 items.
7. **Diff report** for the owner: a short table of what changed vs master and why;
   list any JD must-have with no evidence (gap) — don't paper over it.
8. **Render:** `make cv-app APP=<app dir>`. Open the PDF; check 1–2 pages, no orphans,
   no overflow. Fix and re-render as needed.
9. **Update** `PIPELINE.md` stage → `applying`, commit `app: tailored CV for <company>`.

## Quality bar
- Every bullet: strong verb + concrete what + outcome/scope. No "responsible for".
- No first person, no clichés ("team player", "hard-working"), no photo unless positioning says so.
- ATS-safe: real text (not images), standard section names, no tables for layout-critical text.
