# Frontline (FRO) — decisions log

Why the model is what it is. So neither of us relitigates a settled question,
and the unsettled ones stay visible.

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
- **Tax is negligible.** $554k on $659.7m pre-tax in 2026Q2 — 0.08%.

## Open / weak

- **The Suezmax kernel is the weakest parameter.** Free fit was 12/98 at CV
  3.6%, but a 98-day window lags badly in a fast market, so 25/30 is used at CV
  6.1%. Switching between them swung Q4 by 26%.
- **The back-test is in-sample and single-regime.** Parameters were fitted on
  the same four quarters, and VLCC rose monotonically across all of them
  (34k → 74k → 104k → 153k). Untested against a falling market. Errors aren't
  random-looking either: the two largest are both positive and at the ends.
- **Far outside the calibration range.** Fitted where VLCC ran $34k–$153k. At
  $1.4m/day prints there is no basis for claiming ±6–8% still holds.
- **Three methods disagree on 2026Q3, unresolved.** Coverage $141,000 · kernel
  $158,186 · DHT-implied $162,452. Not a parameter problem — coverage gives
  $135k–$148k across the entire historical k range. Likeliest explanation: no
  quarter in the sample saw an intra-quarter rise like Q3-26, so uncovered days
  may earn a higher fraction than history shows. Hypothesis, not finding.
  **30 November settles it.**
- **Fleet-quality haircut — the live question.** Fearnleys quotes 1-yr T/C for
  modern eco/scrubber tonnage; this fleet is older. At T/C rates the stock
  yields 30.8% at $55.87; a 10% haircut gives 27.4%, a 20% haircut 24.1% — fair
  at today's price. Needs the fleet age profile. Binding question for the
  position.

## Interpolated data

One row in `baltic_weekly.csv` is not a Baltic print: **w/e 2026-08-14**, whose
report was never retrieved. All eight routes are the midpoint of 08-07 and
08-21; the row's `source` says so in capitals.

Filling it moved 2026Q3 from 156,665 → 158,186 (VLCC) and 96,253 → 97,732
(Suezmax), and 2026Q4 from 62.2% → 66.3% observed. If the real report surfaces,
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
  over different week sets (VLCC +5wk, Suezmax +3wk). Corrected to observed.
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
5. **"Observed" counts every week that feeds a quarter, published or not.**
   Dividing by weeks present in the data returns ~100% by construction. This was
   a real bug: it reported 2026Q4 as 94% locked against a true 62%.
6. **One number per question on the dashboard.** It is read on the move, where a
   second number next to the first costs more than it adds. Detail lives here
   and in the forecast table. Do not re-add a "helpful" shadow figure.
