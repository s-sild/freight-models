# freight-models

Rate-driven valuation models. One repo, one site, one model per folder.

```
core/              shared model: blend, recognition kernel, coverage, FCF/implied price
models/frontline/  config.json · data/*.csv · notes.md
model/             extraction and acceptance tests
```

## Weekly routine

| when | source | file | fields |
|---|---|---|---|
| Friday | Baltic Exchange weekly tanker report | `data/baltic_weekly.csv` | TD3C, TD15, TD22, TD34, TD20, TD27, TD33, TD6 |
| Wednesday | Fearnleys weekly | `data/tc_weekly.csv` | VLCC/Suezmax/Aframax 1-yr T/C, fixture count, MEG availability |
| ad hoc | fixture reports | `data/fro_fixtures.csv` | vessel, route, RV TCE, RV days |
| quarterly | Frontline results PDF | `data/fro_quarterly.csv` | spot TCE and days by segment, contracted rate and % covered, breakeven, D&A, adjusted profit |

Add a row, commit. Every row carries a `source`.

## Before anything ships

```
python3 model/validate.py
```

25 checks against figures verified against primary sources. They are not unit
tests of arithmetic — they are the specific numbers this model is known to
produce. If they fail, the change is wrong.

## Read this first

`models/frontline/notes.md` — why each parameter is what it is, what is still
weak, and what was retracted and why.
