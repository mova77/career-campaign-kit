---
name: job-triage
description: Score a job ad or recruiter message against the owner's profile and constraints, decide apply/discuss/decline, and record it in the pipeline. Use whenever a job link, job text, or recruiter approach appears.
---

# Job triage

## Inputs
- The ad (URL → fetch it; text → use it) or recruiter message.
- `profile/positioning.md` (constraints, deal-breakers), `profile/profile.md`,
  `campaign/triage-rubric.md`.

## Procedure

1. **Capture.** Assign the next `O-NNN` ID. If the source is a URL, fetch it and keep the
   full text — ads disappear.
2. **Deal-breaker check** against `positioning.md`. Any hit → score 0, stop, go to step 6.
3. **Unknowns.** List what the ad doesn't say that matters (salary, hybrid days, contract
   type, team size, reporting line). Don't assume the favourable answer.
4. **Company check** (web search if available): size, recent news (layoffs, funding,
   restructuring), review-site signals. Cite sources. Keep it to 3–5 bullets.
5. **Score** each rubric criterion 0–5 with a one-line justification; compute the
   weighted score exactly as the rubric's formula. Map must-have requirements to
   evidence in `profile.md` / `achievements.md`; flag any central must-have the owner
   does not meet.
6. **Output** the rubric block (format in `triage-rubric.md`) + decision.
7. **Record.** Add a row to `PIPELINE.md`. If decision = apply, also run
   `make new-app COMPANY=… ROLE=…`, paste the JD into `job-description.md` and the
   scoring into `fit-analysis.md`.
8. **Recruiter reply** (if it came from a person): draft a reply — for *apply/discuss*,
   ask the open unknowns; for *decline*, a short polite no that keeps the door open.
   Draft only; if Gmail is connected, create a draft, never send.

## Batch mode
Given several ads: produce a ranked table `| O-ID | Company | Role | Score | Decision | Top reason |`
and only create application folders for those scoring ≥ 65 after the owner confirms.
