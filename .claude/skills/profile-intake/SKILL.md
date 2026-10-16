---
name: profile-intake
description: Build or update the verified career profile from LinkedIn exports, old CVs and an interview with the owner. Use at first session, when profile/profile.md still has the TEMPLATE marker, or when new source documents are added.
---

# Profile intake

Goal: a complete, **owner-confirmed** `profile/profile.md` + `profile/achievements.md`,
and from them `cv/data/master.yaml`.

## Inputs
- Everything in `profile/sources/` (LinkedIn PDF, old CVs, other documents).
- The owner, interviewed in small batches.

## Procedure

0. **Stage & import.** Run the `career-stage` classification first: it decides what to dig
   for (first-job → studies, projects, side jobs; veteran → prune and prioritise the last 15 years).
   If a LinkedIn data-export ZIP or a DMA token is available, run
   `tools/linkedin_import.py` (see `docs/linkedin.md`). Treat its `linkedin-draft.yaml`
   as one more **unverified** source, never as truth.
1. **Extract.** Read every source. Build a timeline table:
   `| Period | Title | Company | Source(s) | Conflicts |`.
   Mark conflicts between sources (dates, titles) — don't resolve them yourself.
2. **Show the timeline** to the owner and ask them to confirm/correct it. Only after
   confirmation write the Experience skeleton into `profile.md` (remove the TEMPLATE marker).
3. **Deepen, role by role**, newest first. For each role ask at most 5 questions, e.g.:
   - What did you own — team size, budget, number of projects, stakeholders, geography?
   - Which 1–3 projects are you proudest of? For each: goal, your role, duration, outcome.
   - Anything measurable? (time saved, cost, revenue, quality, satisfaction, delivery on time)
     If they don't know a number, accept a qualitative outcome — **don't suggest numbers**.
   - Tools, methods, certifications used there?
   - What's missing from the old CV that you did since?
4. **Write as you go.** After each answered batch, update `profile.md` with source tag `[user]`
   and add STAR stories to `achievements.md` (`A-01`, `A-02`, …).
5. **Skills audit.** List every skill found; ask the owner to strike any they wouldn't
   defend in an interview.
6. **Generate `cv/data/master.yaml`** following the schema in `cv/data/example.yaml`
   (stage examples: `example-first-job.yaml`, `example-veteran.yaml`), with `stage:` set.
   Bullets: action verb + what + outcome, ≤ 2 lines, from achievements where possible.
7. **Render** with `make cv`, open the PDF, check page count and layout, fix, then show it.
8. **Update state:** tick J-001/J-002 in `BACKLOG.md`, log in `STATE.md`, commit
   `profile: initial verified profile`.

## Done when
- No `<!-- TEMPLATE -->` marker remains; "Open questions" section is empty or explicitly parked.
- Every experience entry has dates, scope and ≥ 1 outcome.
- ≥ 5 STAR stories exist.
- Master CV renders without overflow.

## Don'ts
- Don't upgrade titles ("coordinator" → "manager") unless the owner confirms the real title.
- Don't copy LinkedIn "skills endorsements" wholesale.
- Don't record sensitive personal data (health, family details, ID numbers).
