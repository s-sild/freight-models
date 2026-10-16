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
  $135k–$148k across the entire historical k range.

  Suspected mechanism, and it is about ballast. The two models treat a
  quarter's unfixed tail differently. The kernel handles ballast as **timing
  only**: a week's rate lands on days D+a onward, so ballast days earn nothing,
  but every day that does earn gets the full index. The coverage model handles
  it as a **drag**: uncovered days earn k = 0.27 of the contracted rate,
  calibrated across 17 quarters. On the ~14% of Q3 still unbooked at the report
  date, the kernel says "index, lagged" and coverage says "a quarter of it".
  The kernel being the higher of the two is exactly what that predicts.

  Hypothesis, not finding. The earlier candidate — that no quarter in the
  sample saw an intra-quarter rise like Q3-26, so uncovered days may earn a
  higher fraction than history shows — is still live, and the two are not
  separable with one observation. **30 November settles it**: if realised lands
  near $141k the kernel needs a drag term on its unlocked portion.
- **The locked share is not Frontline's coverage, and it is not a confidence
  measure.** Two separate findings from 16 Oct 2026, both against all 18
  disclosures (`report_date` now carries the publication date of each).

  First, the kernel's locked share and Frontline's disclosed "% covered" are
  different quantities. At the 18 report dates the kernel sits a mean **+14.4
  points** above the disclosure, sd 9.3, range −7.6 to +25.0. The gap does not
  correct away: lengthening the kernel window from 67 days to 120 leaves the
  mean gap at +5.5 to +5.6 throughout, because every report lands 51–60 days
  into the covered quarter (mean 56.7) by which point nearly every feeding week
  is published whatever window is assumed. The kernel asks whether the index
  for a day has printed. Frontline asks whether a fixture exists against that
  day — a commercial choice that ran 68–92% across the sample, correlating
  +0.45 with the contracted rate. The kernel cannot see it.

  Second, and worse for the dashboard: **forecast error does not fall as the
  locked share rises.** Kernel estimate vs realised VLCC spot TCE, 2023Q1
  onward (2022 excluded — the blend prints negative there):

  | locked | n | mean error | mean abs error |
  |---|---|---|---|
  | ~50% | 14 | −3.6% | 10.5% |
  | ~65% | 14 | −4.8% | 8.5% |
  | ~74% | 14 | −5.1% | 8.8% |
  | ~90% | 10 | −5.5% | 10.4% |
  | 100% | 5 | −6.9% | 11.6% |

  Flat. The residual is not in the unpublished weeks; it is in the mapping from
  index blend to Frontline's realised number — fleet age and mix, which voyages
  are actually taken, waiting time. Excluding 2023Q4, which dominates both
  tails (−43% to −27%), the 74% band gives ~6.3% mean absolute error.

  Consequence: a rising locked share does not mean a tightening forecast, and
  waiting for weeks to accumulate does not buy accuracy. The 30 November report
  matters because it supplies Q3 actual and Q4 contracted rate plus coverage —
  hard disclosure — not because more Baltic weeks will have printed.
  Caveats: n=14, bands are coarse enough that a quarter can skip one, and the
  kernel parameters were fitted on 2025Q4–2026Q2, so this is not out-of-sample.

- **BUG, found 17 Oct 2026, not yet fixed: the kernel factor is applied to
  typed anchors.** Press "At base case" — every unpublished week at the slide's
  140 — and the forecast quarters read **147,000**, which is 140,000 x 1.05.
  The kernel's factor exists to convert *Baltic benchmark* into *Frontline
  realised*. 140 is already a Frontline realised number, off their own cash
  generation slide, so the preset converts an already-converted rate.

  It fails its own check: the base-case preset should reproduce the slide by
  construction and does not.

  | | FCF/share | price @ 24% |
  |---|---|---|
  | slide's own base case | $10.35 | $43.12 |
  | what the preset gives | $10.94 | $45.59 |

  5.7% high. "At 1-yr T/C" has the same defect — 225 is a Fearnleys charter
  rate, what Frontline would receive, and gets marked to 236.25. Only "Hold at
  last week" is legitimate, since that injects the Baltic blend, which does
  need converting.

  Fix: apply the factor at series construction, on observed Baltic weeks only,
  not inside `Kernel.quarter`. That also makes the printed-weeks rate and the
  forecast consistent. The gap box is unaffected — it goes straight to the FCF
  model without passing through the kernel. Re-pin the kernel tests after.

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
6. **The panel shows covered, never locked.** `covered = elapsed + phi(1-elapsed)`,
   phi = 0.447 from the 18 disclosures, reproducing them to 3.85 points mean
   absolute error. It is what Frontline itself reports, so 30 November can
   check it. The kernel's locked share stays inside the kernel as a weight and
   is never displayed: it has no company meaning, and forecast error does not
   fall as it rises. Note it was never used in the TCE arithmetic either —
   `tce = Σ(w·rate)/Σw` over published weeks — it was only ever a display
   output we mistook for a diagnostic.
7. **One number per question on the dashboard.** It is read on the move, where a
   second number next to the first costs more than it adds. Detail lives here
   and in the forecast table. Do not re-add a "helpful" shadow figure.
