# Frontline (FRO) — decisions log

Why the model is what it is. So neither of us relitigates a settled question,
and the unsettled ones stay visible.

**For what the model currently does, read `METHOD.md`** — the chain end to
end, every constant marked disclosed / measured / fitted / assumed, and the
variables that could break it. This file is the history and the reasoning;
where the two disagree, METHOD.md is the code and this is the archaeology.

## Settled

- **MEG weight 12%.** Solved from reported TCE, not assumed: 10% implied by
  2026Q2, 15% by 2026Q3.
- **Kernel VLCC 32/35, Suezmax 25/30.** Revenue is recognised ratably from
  commencement of loading to completion of discharge; ballast earns nothing. A
  cargo fixed in week D is recognised across [D+32, D+67). Back-test errors vs
  reported: VLCC +8 / −2 / −1 / +6%, Suezmax +1 / +11 / −1 / +6%.
- **Coverage k = 0.27.** Back-tested across 17 quarters: implied k ranges −0.055
  to +0.591, mean 0.297, median 0.275. Calibrated, not assumed.
- **Required yield 24%.** On 28 Aug 2026, the day the cash-generation slide was
  published, FRO closed at $41.40 against the slide's own $10.35 base-case FCF
  per share — a 25.0% cap rate. 24% sits a point inside the market's number.
- **Day-weight, always.** The six logged fixtures day-weight to $430,376/day;
  the plain average gives $507,282, 18% high, because top rates come on short
  MEG voyages and low ones on long Atlantic hauls. This caused a $250m vs
  $195.4m error once.
- **The realised uplift lives at series construction, not in the kernel.**
  Found and fixed 17 Oct 2026. The kernel used to multiply its result by 1.05
  (VLCC) / 1.03 (Suezmax), which converts Baltic benchmark into what Frontline
  reports. But the forecast feeds typed anchors through the same kernel, and a
  typed anchor is already an owner-level rate. So "At base case" turned the
  slide's own 140 into 147 and returned $10.94/share against the slide's
  $10.35 — the preset could not reproduce the thing it was named after. "At
  1-yr T/C" had it too: 225 is a Fearnleys charter rate, marked to 236.25.

  The uplift now applies to observed Baltic weeks only, at series construction
  (`uplift()` in both model files, `realised_uplift` in config). Kernel factor
  is gone. Consequence: every rate in the forecast section is Frontline-
  realised, so "Hold at last week" shows 764 rather than the benchmark's 728.
  The spot tile and the benchmark chart stay benchmark, which is what they say
  they are.

  All 35 pinned values were unchanged by the move — they are computed from
  observed weeks only, which is what proves the refactor was behaviour-
  preserving everywhere except the bug. Two tests added: the base-case anchor
  must read back unchanged, and an observed week must still be uplifted.

- **Tax is negligible.** $554k on $659.7m pre-tax in 2026Q2 — 0.08%.
## Open / weak

**The live list of parameters and their status is `METHOD.md`.** This section
holds the reasoning, not the register — don't maintain both.

### Still open

- **The uplift is applied three times outside its calibration range.** 1.02 is
  measured on blends from 30k to 150k. Q4 2026 is being priced off a blend of
  475k. `corr(rate level, ratio) = +0.02` says capture does not fade across the
  range we can see, but that says nothing about outside it. **Everything rests
  here.** Frontline's disclosed Q4 covered rate, out with the Q3 report in late
  November, is the direct test.
- **`a` = 14 is the last pure curve fit.** The measured ballast leg is 27.5
  days (17 fixtures, `data/voyage_cycle.md`), and substituting it worsens the
  back-test from 10.9% to 13.7% mean absolute error. So 14 stays, unexplained.
  It is not the ballast leg — it is a statistical lag between a Baltic weekly
  assessment and the earnings it predicts, and the market's autocorrelation is
  the likely reason the fitted value is shorter than the physical one.
- **Suezmax is weak in three places at once.** The basket is not one
  consistent series (11 of 236 weeks carry all three routes), so its 1.03
  uplift cannot be measured the way VLCC's 1.02 was; its kernel 20/44 is scaled
  from VLCC with no voyage splits to measure against; and TD27/TD33 backfill
  from the archived weeklies is still the real fix for the first of those.
- **We disagree with consensus by 4.8x on Q4 2026.** $7.52 against $1.58. See
  `METHOD.md` for why that reads as a stale estimate rather than a considered
  one — chiefly that consensus Q4 implies a VLCC spot TCE below what is already
  locked in printed weeks, and has not moved since before the spike. It is the
  only independent check available and it disagrees, so it is recorded, not
  explained away.

### Closed since

- **"The kernel fills too fast and front-runs a falling market."** The premise
  that drove a month of work. It did not survive a walk-forward test: standing
  at day 20 of each past quarter, falling markets came out mean -2%, median
  +4%, n=5. The error was never in the fill. Every fix aimed at it — a 0.816
  cap, a 0.966 cap, a 7-day lag, the measured a=27 — either failed its own test
  or corrected a number nothing used.
- **Three methods disagreed on 2026Q3.** Resolved by routing rather than
  reconciliation: a quarter Frontline has disclosed is priced with `coverage()`
  (3% mean absolute error over 17 quarters) and the kernel is not consulted.
  The kernel is for quarters with no disclosure, which is the only place it has
  to be used. Consensus independently puts Q3 at $2.27 EPS against the model's
  $2.42.
- **The locked share is not Frontline's coverage.** Still true, now handled by
  naming it: the panel shows **fed**, defined as the share of a quarter's
  earnings whose Baltic week has printed. See rule 6.
- **The back-test was pinned to frozen model outputs.** It now checks against
  what Frontline reported: 2.9% mean absolute error across 2025Q3-2026Q2.

## Interpolated data

One row in `baltic_weekly.csv` is not a Baltic print: **w/e 2026-08-14**, whose
report was never retrieved. All eight routes are the midpoint of 08-07 and
08-21; the row's `source` says so in capitals.

Filling it moved 2026Q3 from 156,665 → 158,186 (VLCC) and 96,253 → 97,732
(Suezmax), and 2026Q4 from 62.2% → 66.3% locked. If the real report surfaces,
replace the row and re-pin those tests.

## Retracted

- **Kpler chokepoint rows — fabricated.** Hormuz and Bab el-Mandeb transit
  counts in the old workbook were invented, not sourced. Deleted, not ported.
  Must be re-sourced from scratch if ever wanted.
- **Spot ÷ T/C ratio.** Compared Atlantic-only spot to a global T/C index. Wrong
  level, contaminated direction. Everything drawn from it was withdrawn.
- **"Atlantic beats all-route."** Before 2026Q2 the baskets were within a few
  thousand dollars — the 2024Q1 spread was *minus* $370 — so they were
  statistically indistinguishable over the calibration window.
- **Quarterly Suezmax/VLCC ratio on the "feeds" basis.** Divided averages taken
  over different week sets (VLCC +5wk, Suezmax +3wk). Corrected to locked.
- **DHT proxy — dropped by choice, not because it was wrong.** DHT publishes a
  Business Update ~2 weeks after quarter end with realised spot TCE and
  next-quarter bookings: a six-week lead on Frontline. But over 8 quarters the
  FRO/DHT ratio averaged 0.972 with 9.4% CV and 7.7% mean absolute error — no
  better than our own kernel. Timing, not accuracy, and two estimates that
  disagree without resolving each other are a decision problem, not an edge.

  | qtr | FRO | DHT | ratio |
  |---|---|---|---|
  | 2024Q3 | 39,600 | 43,700 | 0.906 |
  | 2024Q4 | 35,900 | 38,200 | 0.940 |
  | 2025Q1 | 37,200 | 36,300 | 1.025 |
  | 2025Q2 | 43,100 | 48,700 | 0.885 |
  | 2025Q3 | 34,300 | 38,700 | 0.886 |
  | 2025Q4 | 74,200 | 69,500 | 1.068 |
  | 2026Q1 | 103,500 | 91,700 | 1.129 |
  | 2026Q2 | 152,700 | 162,600 | 0.939 |
  | 2026Q3 | — | 167,100 | — |

## Rules

1. **No citation, no cell.** Blank means not disclosed — never zero, never an
   estimate dressed as data. The one exception is flagged in `source`.
2. **Day-weight, never equal-weight**, across voyages or quarters of unequal
   length.
3. **Frontline does not disclose time-charter days.** Only spot days and
   contracted ballast days. Anything needing TC days stays blank.
4. **Tests pass before anything ships.** `python3 model/validate.py`.
5. **The locked share counts every week that feeds a quarter, published or not.**
   Dividing by weeks present in the data returns ~100% by construction. This was
   a real bug: it reported 2026Q4 as 94% locked against a true 62%.
6. **Name the quantity on the panel, because there are two.** The tile shows
   **fed** — the share of a quarter's earnings whose Baltic week has printed,
   the kernel's own `locked`. That is NOT Frontline's "% covered", which counts
   days on a contracted voyage and reads ~18 points lower at the same date.
   Both are legitimate; conflating them cost a month. If a coverage figure is
   ever displayed alongside, label both.
   *(Replaces the old rule, which said the panel shows covered and never
   locked, and quoted phi = 0.447 where the config said 0.397 — the rule had
   drifted from the code it described.)*
7. **One number per question on the dashboard.** It is read on the move, where a
   second number next to the first costs more than it adds. Detail lives here
   and in the forecast table. Do not re-add a "helpful" shadow figure.
