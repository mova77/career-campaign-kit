---
name: career-stage
description: Adapt the whole campaign (CV shape, search channels, triage weights, interview focus) to the owner's career stage — first job, early career, mid, senior/veteran, executive, returner, or career changer. Use during profile intake, when positioning is set, or whenever advice should differ by seniority.
---

# Career-stage playbooks

## 1. Classify (once, at intake; record in `profile/positioning.md › Career stage`)

| Stage | Signal | CV `stage:` |
|---|---|---|
| First job | Student / graduate, < 1 year full-time work | `first-job` |
| Early | 1–4 years | `early` |
| Mid | 5–12 years, individual contributor or first-line lead | `mid` |
| Senior / veteran | 12+ years, or lead of leads | `senior` |
| Executive | Director+, P&L owner, board exposure | `executive` |
| Returner | Coming back after a break of ≥ 6 months (any seniority) | `returner`, or the seniority stage plus the `return-to-work` skill |
| Career changer | Moving to a new function/industry where direct experience is thin | `career-changer` |

Ask, don't guess, when it's borderline. Stages combine: a senior returner uses `senior` for the CV and `return-to-work` for timing and framing.

## 2. Playbooks

### First job
- **Raw material is everywhere:** thesis, coursework projects, student associations, part-time jobs, volunteering, competitions, Erasmus. Intake must dig into these with the same STAR rigour as jobs.
- **CV:** `stage: first-job` (education → projects → experience). 1 page. Grades only if strong. Part-time jobs stay: they prove reliability; frame transferable outcomes (training others, handling cash, customer conflict).
- **Never** inflate: an internship is an internship, a group project credits the group ("in a team of 4, I built…").
- **Channels:** graduate programmes and internships (often with fixed annual deadlines, so track them in `STATE.md › Key dates`), university career offices and job fairs, alumni on LinkedIn, entry-level job boards.
- **Triage tweak:** raise *Growth* weight to 3, lower *Compensation* to 1. Mentoring and training count more than salary deltas at this stage.
- **Interview focus:** motivation, learning speed, examples from studies and side jobs, basic case/technical tests. Practise the "tell me about yourself" story hardest.
- **LinkedIn:** headline = target role + degree + 2–3 hard skills. Ask lecturers and internship managers for recommendations.

### Early career (1–4 y)
- **CV:** experience first, projects still allowed. 1 page. Education compressed to one line unless very relevant.
- Show trajectory: increasing scope, promotions, ownership.
- **Triage:** default weights. Watch for "junior" roles that are senior workloads at junior pay.

### Mid career (5–12 y)
- **CV:** default layout, up to 2 pages. Bullets must show outcomes, not duties.
- Pick a lane: specialist depth vs. move to management. `positioning.md` must say which, and triage enforces it.

### Senior / veteran (12+ y)
- **CV:** `stage: senior`. *Selected achievements* (3–4 lines) at the top. Detail only the last ~12–15 years. Older roles go into `earlier_career` as one-liners. Graduation years are optional; leave them out if the owner prefers.
- **Counter age bias with currency:** recent tools, methods and results. Keep "30 years of experience" and other dated phrasing out of the headline; lead with scope and outcomes.
- **Channels:** network first (former colleagues, ex-managers, suppliers and clients), specialist recruiters, interim/fractional roles, advisory work. Job boards come last.
- **Triage:** raise *Company quality* and *Career direction*. Treat a big title at a weak company as a red flag.
- **Interview focus:** leadership philosophy with evidence, handling of failure, stakeholder and board dynamics, and "why not retire / why this step" answered with energy and specifics.
- **Salary:** anchor on total package and the scope of the role. Avoid quoting first when possible.

### Executive
- As senior, plus: a 1-page executive bio alongside the CV, board/advisory roles in their own section (use `projects` or `highlights`), confidentiality about the current employer. Searches often run through executive-search firms, so maintain a short list of them in `campaign/`.

### Returner
- Use the `return-to-work` skill for timeline, notice and framing.
- **CV:** the break is one neutral line or nothing. Refresh activities (courses, volunteering, projects) go in `projects`/`certifications` only if they're real.
- **Channels:** "returnship" programmes, previous employers and colleagues (warm channel, high conversion).
- **Triage:** *Flexibility* weight 3 if new constraints exist. Constraints are recorded, not hidden.

### Career changer
- **CV:** `stage: career-changer` (highlights → projects → experience). Highlights translate past results into the new field's language. Projects prove hands-on work in the new field (courses with deliverables, side projects, pro-bono work).
- Be explicit about the bridge: what transfers, what was learned, what's still missing.
- **Triage:** accept a step down in title if it's a step up in direction. Score *Career direction* at weight 4.

## 3. Applying it
- Set `stage:` in `cv/data/master.yaml`. Per application, override with `sections:` if a JD calls for a different emphasis.
- Copy the stage's triage tweaks into `campaign/triage-rubric.md › Weights in use` and log the change as an ADR.
- Revisit the stage when the situation changes (first job landed, promotion, break started).
