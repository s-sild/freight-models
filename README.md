# freight-models

Rate-driven valuation models. One model per folder.

```
core/              blend · recognition kernel · coverage · FCF/implied price
models/frontline/  config.json · data/*.csv · notes.md · index.html
model/             extraction and acceptance tests
```

## Weekly

| when | file | fields |
|---|---|---|
| Friday | `data/baltic_weekly.csv` | TD3C TD15 TD22 TD34 TD20 TD27 TD33 TD6 |
| Wednesday | `data/tc_weekly.csv` | VLCC / Suezmax / Aframax 1-yr T/C, fixture count, MEG availability |
| ad hoc | `data/fro_fixtures.csv` | vessel, route, RV TCE, RV days |
| quarterly | `data/fro_quarterly.csv` | spot TCE and days by segment, contracted rate and % covered, breakeven, D&A, adjusted profit |

Add a row, commit. Every row carries a `source`.

## Before shipping

```
python3 model/validate.py
```

28 checks pinning figures verified against primary sources — the kernel
back-test, implied k across 17 quarters, the implied-yield series, the T/C
basis. Not unit tests of arithmetic. Re-pin them only when an input
deliberately changes, or they stop catching anything.

## Read first

`models/frontline/notes.md` — what each parameter is and why, what is still
weak, and what was retracted.
