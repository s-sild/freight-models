# How the forecast works

One page. Every constant below is either disclosed by Frontline, measured
against disclosures, or named as unmeasured.

---

## Step 1 — Baltic routes to one blend

```
VLCC     = 0.88 x mean(TD15, TD22) + 0.12 x TD3C
Suezmax  = mean of TD20 / TD27 / TD33 present that week
```

A route with no print that week is **excluded from the average, never counted
as zero**. Blank means not disclosed.

The 12% MEG weight is solved from reported TCE: 10% fits 2026Q2, 15% fits
2026Q3, 12% adopted.

These are round-voyage TCEs. **Ballast is already inside them** — they are per
available day of the voyage, the same basis as Frontline's reported TCE
(total spot earnings / total spot days).

*Weak spot: the Suezmax basket is not one consistent series. Of 236 weeks only
11 carry all three routes, 133 are TD20 alone. TD33 first appears 2026-08-07.*

## Step 2 — Blend to owner-realised rate

```
VLCC x 1.02        Suezmax x 1.03
```

Applied at series construction, to **printed weeks only**. Never inside the
kernel, and never to a forecast anchor you type — that is already an
owner-level rate, and marking it up again was the 140 -> 147 bug.

Both are MEASURED over the 9 post-Euronav quarters 2024Q3-2026Q3:
VLCC mean **1.012** sd 0.048, Suezmax mean **1.026** sd 0.053.

Suezmax was previously carried as an unmeasured 1.03. It is now measured and
the number barely moved — but its basket composition shifts over the window
(TD33 only from 2026-08-07), so the denominator is not one consistent series.

Capture does NOT fall at high rates. 2026Q3 came in at 0.943, which was the
feared failure, but `corr(blend level, ratio) = -0.30` at n=9 and the two
lowest ratios in the sample are 0.937 at a blend of 36,618 and 0.943 at
157,473. Both ends of the range. It is dispersion, not a rate effect.

## Step 3 — Weekly rates to one quarterly rate: the kernel

A cargo assessed in the week ending **D** is recognised across
**`[D+a, D+a+b)`**. Its weight in a quarter is however many of those days fall
inside it.

```
VLCC      a = 14   b = 66
Suezmax   a = 20   b = 44
```

- **`b` is the load-to-discharge window** — Frontline recognises revenue
  ratably from commencement of loading to completion of discharge. It was
  FITTED. The 66.6-day fixture measurement that used to corroborate it was
  wrong (see `data/voyage_cycle.md`, corrected 2026-11-13); on the right basis
  the fixtures give 56.3 days, 15% below. `b` has no independent support.
  Q4 2026 is insensitive at 88% fed, and a shorter window would raise it.
- **`a` is the lag from assessment to earning, NOT the ballast leg.** It is
  FITTED, and it is the last parameter in the chain standing on a curve fit.
  The measured ballast leg is 27.5 days; substituting it worsens the back-test
  from 10.9% to 13.7% mean absolute error, so 14 stays. `a + b` is NOT the
  round voyage — the next cargo is fixed partway through the current one.

**What this looks like for Q4 2026**: 22 weeks feed it, from the week ending
17 July (day 17 of Q3) to 11 December (day 72 of Q4). Weights ramp 4, 11, 18,
25 … up to the full 66 for the weeks ending 18 Sep to 9 Oct, then taper back
to 7. They sum to **867** — not a day count, but the sum of overlaps. 867 / 92
calendar days = 9.4, which is just b / 7: a 66-day window spans 9.4 weekly
cohorts, so nine weeks of cargoes earn simultaneously on any given day.

A gap in the series **at or before the last print is a UK holiday** — the
Baltic never published it and never will. It is dropped from the denominator,
not treated as pending. Gaps after the last print are genuinely pending.

## Step 4 — Printed weeks and the forward curve

```
rate = locked x (printed-week rate) + (1 - locked) x (forward curve)
```

`locked` is the **share of the quarter's day-weight already printed** — the
kernel's own number, which it computes anyway.

This is the panel's headline percentage, labelled **"fed"**:

> share of the quarter's earnings whose Baltic week has already printed

**It is not Frontline's "% covered"**, which counts days on a contracted
voyage. At day 58 coverage reads ~79% where this reads ~97%, because the
uncovered fifth is mostly ballast and earns about a quarter as much. Using the
coverage figure as the blend weight put 39% of Q4 on the forward curve when
17% of the feed was unprinted. That was phi = 0.397, now removed.

A completed quarter has `locked = 1`, so the back-test is untouched.

## Step 5 — Disclosed quarters skip steps 1-4 entirely

```
realised = contracted x (cov + (1 - cov) x k)
k:  VLCC 0.26    Suezmax 0.55    Aframax 0.45
```

When Frontline has published a covered rate and a covered % for a quarter —
always the nearest unreported one, since those come out with the previous
quarter's report — **use their numbers, not ours**. The coverage model
back-tests at 3% mean absolute error against the kernel's 11%.

`k` is the share of the contracted rate the uncovered days earn, measured over
18 quarters as a median. **Its spread matters more than its level**: VLCC sd is
0.175 on a median of 0.280, which on the 2026Q4 disclosure is worth +/-31,400
a day, about 0.5 of adjusted EPS. It does not scale with the rate —
`corr(contracted rate, k) = +0.02`, and the three highest-rate quarters gave
0.58, 0.11 and 0.62. Treat any single-point output of step 5 accordingly. The ordering follows voyage length: Suezmax `b` = 44 against
VLCC 66, so a cargo fixed after the report date lands more of its window
inside the quarter and the Suezmax tail is less ballast-heavy.

The forecast window **opens on that quarter and rolls forward one when
Frontline reports**. It is frozen — the forward-curve presets cannot move it.

## Step 6 — Rate to earnings and EPS

```
spot revenue = VLCC spot days x VLCC TCE
             + other spot days x (54% Suezmax + 46% LR2)
TC revenue   = TC days x the contracted charter rate
EPS          = (total TCE - 173.1) / 222.62
```

Day counts are **disclosed** (`data/earnings_days.csv`, Q2 2026 report, 12m
forward from 28 Aug). The 54/46 split of non-VLCC spot days is the ratio of
2026Q2 actuals. The 173.1 gap is TCE less adjusted profit, calibrated on
2026Q2 and held flat — largely fixed cost, but it will understate the gap if
the fleet grows.

The output is adjusted EPS, and the declared dividend has equalled adjusted
EPS to the cent in every quarter checked (0.19, 1.03, 1.55, 2.61). While that
policy holds, this is also the dividend forecast.

---

# The variables to check

Ordered by how much damage a wrong value does.

| # | variable | status | how it fails |
|---|---|---|---|
| 1 | **`k` spread** | median over 18q, sd 0.175 | Step 5 now prices Q4 off Frontline's own disclosure, so k IS the forecast. One sd is +/-31,400/day, about 0.5 of adjusted EPS, and k does not scale with the rate. The single biggest source of error in the current number. |
| 2 | **`a` = 14** | FITTED, not measured | The last curve fit. `b` = 66 lost its fixture corroboration on 2026-11-13 (voyage_cycle.md), so both kernel parameters now stand on the fit alone. |
| 3 | **Suezmax kernel 20/44** | SCALED from VLCC | No Suezmax fixture has ever entered the sample. 26 voyages in voyage_splits.csv, all VLCC, while Suezmax fell 51% in the week to 2026-11-06. Weakest leg carrying the most recent movement. |
| 4 | **Suezmax basket** | inconsistent series | Of 236 weeks only 11 carry all three routes; TD33 starts 2026-08-07. The uplift is now measured on it, but the denominator changes composition. |
| 5 | **54/46 non-VLCC day split** | one quarter | From 2026Q2 actuals only. |
| 6 | **forward day counts** | Q2 2026 vintage | `earnings_days.csv` is the 12m window disclosed on 2026-08-28. Two VLCCs sold, two newbuildings delivered in Q4 and a Suezmax put on a 3-year charter since. Not refreshed - the Q3 press release does not carry the forward table. |

**RESOLVED 2026-11-20 by the Q3 report.** The uplift extrapolation that was
variable 1 did not fail: 2026Q3 capture was 0.943 against a mean of 1.012, but
`corr(blend level, ratio) = -0.30` and 0.937 occurred at a blend of 36,618.
Dispersion, not a rate effect. The TCE-to-profit gap (0.1% off), the charter
rate (1.1%) and the whole EPS bridge (Q3 EPS 2.42 against 2.38) all held. The
one thing that missed was the rate forecast, by +8.2%.

**The near-term test.** Q4 2026 reports late February 2027. Q4 is 92% fed and
priced off Frontline's disclosure (VLCC 562,600 at 68% covered), so it mostly
tests `k`. The open quarter is **Q1 2027** - 10% fed on VLCC, 4% on Suezmax,
and the quarter the 2026-11-13 collapse actually lands in.

**Where we disagree with the market.** Both figures below are **adjusted**
EPS, the basis this model produces and the one Frontline's normalized
consensus is quoted on. GAAP is a different number - 2.51 against 1.55
adjusted in 2026Q1 - so a GAAP series is not a comparator.

Consensus Q4 EPS is $1.58. Off Frontline's own disclosure, Q4 lands near
$6.50-8.00 depending on `k`, and the quarter is 92% fed. Working backwards,
$1.58 implies a Q4 VLCC spot TCE near $92,000/day against 562,600 already
contracted on 68% of the days. It has not moved since before the spike began
(1.40 / 1.60 / 1.58 / 1.58 / 1.58 at 90/60/30/7/0 days) while the Q3 figure
rose 1.38 -> 2.27 and then reported 2.38. **Two** analysts carry the Q4 cell.
Read it as stale rather than considered - but it is the only independent check
available.
