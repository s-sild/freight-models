# Frontline (FRO) — decisions log

Why the model is built the way it is. Written so neither of us relitigates
settled questions, and so the unsettled ones stay visible.

---

## Settled

**MEG weight = 12%.** Solved from reported TCE, not assumed: 10% implied by
2026Q2, 15% by 2026Q3. TD3C is weighted separately from TD15/TD22 because
Frontline's exposure to the MEG route differs from an equal-weighted index.

**Kernel: VLCC a=32 / b=35, Suezmax a=25 / b=30.** Revenue is recognised
ratably from commencement of loading to completion of discharge — ballast days
earn nothing. So a cargo fixed in week D is recognised across [D+32, D+67).
Fitted on 2024Q1–2026Q2. Back-test errors against reported TCE: VLCC +8%, −2%,
−1%, +6%; Suezmax +1%, +11%, −1%, +6%.

**Coverage model k = 0.27.** At the report date, X% of the quarter is contracted;
the uncovered remainder earns k × that rate. Back-tested across **17 quarters** of
disclosure: implied k ranges −0.055 to +0.591, mean 0.297, median 0.275. 0.27 is
effectively the median, so it is calibrated rather than assumed.

**Required yield 24% is not arbitrary.** On 28 August 2026 — the day Frontline
published the cash-generation slide — FRO closed at $41.40 against the slide's own
$10.35 base-case FCF per share. That is a 25.0% cap rate. 24% sits a point inside
the market's own number.

**Day-weight fixtures, always.** The six logged fixtures day-weight to
$430,376/day; the plain average gives $507,282 — 18% too high, because the top
rates are short MEG voyages and the low ones are long Atlantic hauls. This caused
a $250m vs $195.4m error once already.

**Tax is negligible.** $554k on $659.7m pre-tax in 2026Q2 — 0.08%.

---

## Open / weak

**The Suezmax kernel is the weakest parameter in the model.** The free fit was
a=12 / b=98 at CV 3.6%, but a 98-day window averages three and a half months of
rates and lags badly in a fast market, so the physical-looking 25/30 is used
instead at CV 6.1%. Changing between them swung Q4 by 26%.

**The kernel back-test is in-sample and single-regime.** Parameters were fitted
on the same four quarters. And VLCC went 34k → 74k → 104k → 153k across the
window — monotonically up. A lag structure that tracks a rising market is not
tested against a falling one. The errors are not random-looking either: +8%, −2%,
−1%, +6%, with the two largest both positive and at the ends.

**Extrapolation far outside the calibration range.** The kernel was fitted where
VLCC ran $34k–$153k. At $1.4m/day prints there is no basis to claim the ±6–8%
error band still holds.

**Three methods disagree on 2026Q3 and it is unresolved.** Coverage model
$141,000 · kernel $156,665 · DHT-implied $162,452. The disagreement is not a
parameter problem — the coverage estimate is $135k–$148k across the entire
historical k range. Most likely explanation: no quarter in the sample saw an
intra-quarter rise like Q3-26, so uncovered days may earn a higher fraction of
contracted than history has ever shown. That is a hypothesis, not a finding.
**30 November settles it.**

**Fleet-quality haircut — the live question.** Fearnleys quotes 1-yr T/C for
*modern ECO/scrubber* tonnage. Frontline's fleet averages older, especially the
Euronav ships. At the T/C rates the stock yields 30.8% at $55.87; a 10% haircut
makes it 27.4%, a 20% haircut 24.1% — fair at today's price. Cannot be sized
without the fleet age profile. This is now the binding question for the position.

---

## Retracted / removed

**Kpler chokepoint rows — I fabricated them.** Hormuz and Bab el-Mandeb transit
counts in the old workbook were invented, not sourced. Deleted, not ported. If
that data is ever wanted it must be re-sourced from scratch.

**Spot ÷ T/C ratio.** Compared Atlantic-only spot against a global T/C index.
Wrong level, and the direction was contaminated too. Any inference drawn from it
was withdrawn.

**"Atlantic beats all-route" sweep.** Before 2026Q2, TD3C and the Atlantic routes
were within a few thousand dollars of each other — the 2024Q1 spread was *minus*
$370 — so the baskets were statistically indistinguishable over the calibration
window. The conclusion was unsupported.

**Quarterly Suezmax/VLCC ratio on the "feeds" basis.** Divided averages taken
over different week sets (VLCC +5wk, Suezmax +3wk). Corrected to the observed
basis.

**DHT proxy — dropped by choice, not because it was wrong.** DHT Holdings is a
pure-play VLCC owner that publishes a Business Update ~2 weeks after quarter end,
giving realised spot TCE and next-quarter bookings — a six-week lead on Frontline.
Over 8 quarters the FRO/DHT ratio averaged 0.972 with 9.4% CV and 7.7% mean
absolute error: **no better than our own kernel**. Its value was timing, not
accuracy, and two estimates that disagree without resolving each other are a
decision problem rather than an edge. Series kept here for reference only:

| quarter | FRO | DHT | ratio |
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

---

## Rules

1. **No citation, no cell.** Every data row carries a source. Blank means not
   disclosed — never zero, never an estimate dressed as data.
2. **Day-weight, never equal-weight**, any time rates are averaged across
   voyages or quarters of unequal length.
3. **Frontline does not disclose time-charter days.** Only spot days and
   contracted ballast days. Anything requiring TC days stays blank.
4. **Acceptance tests must pass before anything ships.** `python3 model/validate.py`.
