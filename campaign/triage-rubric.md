# Triage rubric

Each criterion is scored 0–5, multiplied by its weight; total normalised to 0–100:

$$S = \frac{100}{5\sum_i w_i}\sum_i w_i\,s_i, \qquad s_i \in \{0,\dots,5\}$$

Any **deal-breaker** from `profile/positioning.md` ⇒ score 0, stage `declined`, regardless of the rest.

| # | Criterion | Weight $w_i$ | 0 = | 5 = |
|---|---|---|---|---|
| 1 | Role fit — must-have requirements met | 3 | < 50 % of must-haves | all must-haves, most nice-to-haves |
| 2 | Career direction — moves towards target in positioning.md | 3 | sideways/backwards | exactly the target |
| 3 | Compensation vs floor/target | 2 | below floor or undisclosed with red flags | at/above target |
| 4 | Flexibility — location, hybrid days, hours | 2 | violates constraints | fully fits |
| 5 | Company quality — stability, reputation, culture signals | 1 | serious red flags | strong signals |
| 6 | Growth — learning, scope, promotion path | 1 | none visible | explicit |
| 7 | Process cost — effort to apply, clarity of recruiter | 1 | opaque / excessive | clear and light |

### Stage presets (weights for criteria 1–7)

| Stage | Fit | Direction | Comp. | Flex. | Company | Growth | Process |
|---|---|---|---|---|---|---|---|
| default / mid | 3 | 3 | 2 | 2 | 1 | 1 | 1 |
| first-job | 2 | 2 | 1 | 2 | 1 | 3 | 1 |
| early | 3 | 3 | 2 | 2 | 1 | 2 | 1 |
| senior / executive | 3 | 3 | 2 | 2 | 2 | 1 | 1 |
| returner | 3 | 3 | 2 | 3 | 1 | 1 | 1 |
| career-changer | 2 | 4 | 1 | 2 | 1 | 2 | 1 |

**Weights in use:** default (change via the `career-stage` skill and record the change in an ADR)

**Thresholds:** ≥ 65 apply · 50–64 discuss with owner · < 50 decline (politely, if there's a recruiter to answer).

**Hard rule:** if a requirement listed as *mandatory* would be learned on the job and is central to the role, flag it explicitly — don't bury it in the average.

Output format the `job-triage` skill must produce:

```
O-NNN  <Company> — <Role>
Score: NN/100   Decision: apply | discuss | decline
| # | Criterion | s | note |
Red flags: …
Unknowns to ask the recruiter: …
```
