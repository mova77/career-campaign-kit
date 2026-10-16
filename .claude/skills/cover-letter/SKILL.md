---
name: cover-letter
description: Write a cover letter, motivation letter, or application-form free-text answers for one specific application, grounded in verified achievements. Use when an application asks for a letter or written answers.
---

# Cover letter

## Inputs
`<app>/job-description.md`, `<app>/fit-analysis.md`, `profile/achievements.md`,
`profile/positioning.md`, company research (web search if available).

## Structure (≤ 300 words unless the employer asks for more)
1. **Hook (2–3 sentences):** the role, and one specific reason *this* company — something
   real from research (product, mission, a recent initiative), not generic praise.
2. **Proof (1–2 paragraphs):** two achievements (`A-xx`) mapped to their top two
   must-haves. Situation in one clause, action, result.
3. **Fit & logistics (1–2 sentences):** availability / start date / work-mode fit, if
   it helps. Address a transition or career break only with the line agreed in
   `positioning.md` — briefly and confidently, never apologetically.
4. **Close:** clear call to action.

## Rules
- Language = job ad's language. Match the company's register (startup vs. corporate vs. public sector).
- Every claim traces to `achievements.md` / `profile.md`.
- No repetition of the CV line-by-line — the letter explains *why these facts matter here*.
- Save to `<app>/cover-letter.md`. If a PDF is needed, render the Markdown with the
  same visual theme (ask Claude to produce `cover-letter.html` from `cv/templates/theme.css`).

## Application forms
For free-text form fields, produce `<app>/form-answers.md` with each question verbatim,
the answer, and its character count vs the field limit.
