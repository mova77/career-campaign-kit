# career-campaign-kit

A Claude-driven job-search workspace: your career facts, your CV pipeline, and a set of
specialised agent skills, all in one git repo that Claude reads and maintains with you.

It turns a job search into a managed campaign:

| Layer | What lives there | Who maintains it |
|---|---|---|
| **Profile** (`profile/`) | Your verified career facts, achievements bank, positioning | You + Claude (intake skill) |
| **Campaign** (`campaign/`) | State, pipeline, numbered backlog, decision records | Claude, every session |
| **Applications** (`applications/`) | One folder per opportunity: JD, fit analysis, tailored CV, cover letter, interview notes | Claude, per application |
| **CV engine** (`cv/`) | CV as structured YAML → HTML → PDF | `make cv` |
| **Skills** (`.claude/skills/`) | Intake, triage, CV tailoring, cover letters, LinkedIn, interview prep, career stage, return to work | Loaded by Claude on demand |
| **LinkedIn** (`tools/linkedin_*.py`) | Import your own profile (export ZIP or EU data-portability API), publish posts | `make li-zip` / `make li-api` |

**Built for every career stage:** first job (education, projects and side jobs lead),
early and mid career, senior veterans (highlights up front, earlier career compressed),
executives, returners after a break, and career changers. Each stage gets its own CV
layout, page budget, triage weights and search playbook. See `cv/data/example*.yaml`.

---

## 1. One-time setup (≈15 minutes)

### 1.1 Prerequisites

- **Claude Desktop** (macOS / Windows) with a Pro or Max plan
- **Python 3.10+** and **git**
- Optional: GitHub account (private repo recommended — this will contain personal data)

### 1.2 Create your own copy, then install

This is a **GitHub template repository**. Don't fork it — click **Use this template →
Create a new repository** and set the new repo to **Private** (it will hold your CV and
career data). Or from a terminal:

```bash
gh repo create my-career --template <owner>/career-campaign-kit --private --clone
cd my-career
make setup          # creates .venv, installs deps + Chromium for PDF rendering
make test           # sanity check: should end with "passed"
```

On Windows without `make`: `python -m venv .venv`, activate it, then
`pip install -r requirements.txt && python -m playwright install chromium`.

### 1.3 Drop in your source material

| File | Where | How to get it |
|---|---|---|
| LinkedIn profile (quick) | `profile/sources/linkedin.pdf` | LinkedIn → your profile → **More** → **Save to PDF** |
| LinkedIn profile (structured, best) | `profile/sources/*.zip` → `make li-zip ZIP=…` | Settings → Data privacy → **Get a copy of your data**. EEA/CH members can instead use the API: `make li-api` |
| Old CV | `profile/sources/` (any of .pdf / .docx) | Whatever you have; outdated is fine |
| Anything else useful | `profile/sources/` | Reference letters, performance reviews, project reports, certificates |

`profile/sources/` is git-ignored by default (see `.gitignore`), so raw documents stay on your machine.
LinkedIn setup, including registering your own developer app for the API route, is in [`docs/linkedin.md`](docs/linkedin.md).

### 1.4 Open it in Claude Desktop

Use **either** mode — both work, Mode A is the more powerful one.

**Mode A — Claude Desktop, Code tab (recommended).**
Open the **Code** tab, choose this folder as the working directory. Claude reads
`CLAUDE.md` automatically at the start of every session and the skills in
`.claude/skills/` become available. The repo itself is the memory: state survives
because Claude writes it to `campaign/STATE.md` and commits.

**Mode B — a claude.ai Project.**
1. Create a Project called e.g. *Career Campaign*.
2. Paste the contents of `project/PROJECT_INSTRUCTIONS.md` into the Project's custom instructions.
3. Upload `CLAUDE.md`, everything in `profile/` and `campaign/` as Project knowledge.
4. Turn on memory and *Search and reference chats* in Settings.
5. Connect this folder from the desktop app (**+** → **Add folder**) so Claude can update files.

### 1.5 First session

Start a new chat and paste the prompt in `project/FIRST_SESSION_PROMPT.md`.
Claude runs the **profile-intake** skill: reads your LinkedIn + old CV, interviews you
about what's missing (projects you managed, outcomes, numbers), and produces
`profile/profile.md` and `cv/data/master.yaml`. Expect 2–3 rounds of questions.

---

## 2. Daily use

Talk to Claude normally. Typical requests and what happens:

| You say | Skill used | Output |
|---|---|---|
| "Here's a job ad: <link or text>" | `job-triage` | Fit score, red flags, go/no-go, entry in `PIPELINE.md` |
| "Let's apply to J-007" | `cv-tailor` + `cover-letter` | `applications/<date>-<company>-<role>/` with tailored CV PDF + letter |
| "Rework my LinkedIn" | `linkedin-optimizer` | Headline, About, experience bullets, ready to paste |
| "I have an interview Thursday at X" | `interview-prep` | Company brief, likely questions, STAR answers from your bank |
| "A recruiter wrote me" (paste it) | `job-triage` | Assessment + reply draft (never sent without your OK) |
| "Where are we?" | — | Summary from `STATE.md` + `PIPELINE.md` |

At the end of each working session Claude updates `campaign/STATE.md`, ticks the backlog,
and commits. You can push whenever you like (`git push`).

## 3. Commands

```bash
make cv                                   # render master CV  → cv/out/master.{html,pdf}
make cv-example                           # render the 3 fictional stage examples
make li-zip ZIP=profile/sources/export.zip   # LinkedIn export → draft CV YAML (unverified)
make li-api                               # same via the EU data-portability API
make li-post POST=campaign/posts/x.md     # dry-run a LinkedIn post
make cv-app APP=applications/2026-11-03-acme-pm   # render one application's CV
make new-app COMPANY="Acme" ROLE="Project Manager"   # scaffold an application folder
make test                                 # run the test suite
```

## 4. Principles the agent follows

Written down in `CLAUDE.md`; the short version:

1. **Facts are sacred.** The CV never contains anything not in `profile/profile.md`. No invented numbers, titles, or tools.
2. **Triage before effort.** Every opportunity is scored before any CV work.
3. **Tailor, don't rewrite.** Each application selects and re-orders verified facts; the master stays canonical.
4. **Nothing leaves without you.** Emails, LinkedIn messages and applications are drafted, never sent, unless you say "send".
5. **State is written down.** If it isn't in `campaign/`, the next session doesn't know it.

## 5. Privacy

- Keep the GitHub repo **private**.
- `profile/sources/` and `cv/out/` are git-ignored.
- Never commit ID numbers, bank details, or salary slips. Salary *expectations* belong in `profile/positioning.md` only if you are comfortable with them being in the repo.

## 6. Language

Works in any language. Claude talks to you in the language you write in, and writes each
CV / cover letter in the language of the job ad (or whatever `profile/positioning.md` says).
The CV template's section labels are set per CV in the YAML (`labels:`), so a Polish,
Italian or German CV needs no template change.

## 7. Contributing / improving the template

Improvements to skills, the CV template or tooling are welcome — see `CONTRIBUTING.md`.
Personal data never goes into the template repo; only into your private copy.

## 8. Layout

```
.
├── CLAUDE.md                     # agent operating manual (read every session)
├── project/                      # claude.ai Project instructions + first-session prompt
├── profile/
│   ├── sources/                  # raw LinkedIn PDF, old CVs (git-ignored)
│   ├── profile.md                # canonical, verified career facts
│   ├── achievements.md           # STAR bank used by CVs, letters, interviews
│   └── positioning.md            # target roles, constraints, non-negotiables
├── campaign/
│   ├── STATE.md                  # where things stand (updated every session)
│   ├── PIPELINE.md               # every opportunity and its stage
│   ├── BACKLOG.md                # numbered work items (J-001 …)
│   ├── triage-rubric.md          # weighted scoring model
│   └── decisions/                # ADRs: why we decided what we decided
├── applications/_template/       # copied per application by `make new-app`
├── cv/
│   ├── data/master.yaml          # the master CV, structured (created at intake)
│   ├── data/example*.yaml        # schema references: mid, first-job, veteran
│   ├── templates/                # Jinja2 HTML template + theme
│   └── out/                      # rendered HTML/PDF (git-ignored)
├── docs/linkedin.md              # LinkedIn API/export setup
├── tools/                        # build_cv, new_application, linkedin_import, linkedin_post
├── tests/
├── .mcp.json                     # Microsoft Learn MCP: official LinkedIn API docs for the agent
└── .claude/skills/               # the agent skills
```
