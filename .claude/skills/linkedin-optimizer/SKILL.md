---
name: linkedin-optimizer
description: Rewrite the LinkedIn profile (headline, About, experience entries, skills, open-to-work settings) to match the positioning and verified profile. Use when the owner asks to improve LinkedIn or after positioning changes.
---

# LinkedIn optimizer

## Inputs
`profile/positioning.md`, `profile/profile.md`, `profile/achievements.md`,
current LinkedIn (`profile/sources/linkedin.pdf`).

## Deliverable — `profile/linkedin.md` with copy-paste-ready blocks

| Section | Constraint | Guidance |
|---|---|---|
| Headline | ≤ 220 chars | Target role + domain + 1 proof point. Recruiters search titles: lead with the title they'd type. |
| About | ≤ 2,600 chars; first ~2 lines visible | Line 1–2: who + value. Then 3 short proof paragraphs (A-xx). End: what you're looking for + how to reach you. First person is fine here. |
| Experience | per role | 3–5 bullets, same facts as CV, more conversational. Include projects managed. |
| Skills | up to 50; top 5 pinned | Pin the 5 that match target role titles' typical requirements. |
| Featured | optional | Project write-ups, certificates, articles. |
| Open to work | settings | Recommend recruiter-only visibility vs public based on whether current employer should see it — ask the owner. |

## Procedure
1. Diff current LinkedIn vs `profile.md`; list factual mismatches first (dates, titles).
2. Draft all blocks; show headline in 3 variants for the owner to pick.
3. Bilingual market (e.g. PL/EN): ask which language is primary; LinkedIn supports a
   secondary-language profile — offer to draft it.
4. The owner pastes the text. LinkedIn offers no profile-edit API to individuals. Never
   ask for credentials, and never use session/cookie-based tools (see ADR-0002).
5. Optional announcement post: draft in `campaign/posts/<date>-<slug>.md` and show it
   with `tools/linkedin_post.py <file>` (dry run). Only with `--publish` after the owner
   says "publish" for that post.
6. Commit `profile: linkedin copy vN`.

Stage nuances come from the `career-stage` skill (e.g. first-job headline = target role + degree + skills).
