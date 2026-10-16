# Contributing

Thanks for improving the kit! Two kinds of repos exist:

- **The template** (this repo, public): skills, tooling, CV template, docs. **No personal data, ever.**
- **Your instance** (created via *Use this template*, private): your profile, applications, state.

## Workflow

1. Open an issue describing the problem or improvement.
2. Branch from `main`: `feat/<topic>`, `fix/<topic>`, `docs/<topic>`.
3. Conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
4. `make test` must pass; add tests for any change in `tools/` or `cv/templates/`.
5. If you change a skill, include a short before/after example of the agent's output in the PR.
6. PRs need one review; squash-merge.

## Skill authoring guidelines

- One skill = one job. State the trigger, inputs, procedure, output format, and done-criteria.
- Skills must respect the rules in `CLAUDE.md §1` (facts are sacred, draft-don't-send).
- Keep skills language-neutral; the agent writes in the user's / the job ad's language.

## Upstream updates into your instance

```bash
git remote add template https://github.com/<owner>/career-campaign-kit.git
git fetch template
git merge template/main --allow-unrelated-histories   # first time only needs the flag
```
Conflicts will only occur in files you've customised (usually `CLAUDE.md` or the rubric).
