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

**1.02 is measured**: realised VLCC TCE / blend over the 8 post-Euronav
quarters is mean 1.020, sd 0.044. It reads 1.020 at a blend of 101,437
(2026Q1) and 1.018 at 150,097 (2026Q2). `corr(rate level, ratio) = +0.02`.

*Weak spot: 1.03 for Suezmax is NOT measured on the same basis — the basket
above makes the ratio uncomputable. It is carried forward unchanged.*

## Step 3 — Weekly rates to one quarterly rate: the kernel

A cargo assessed in the week ending **D** is recognised across
**`[D+a, D+a+b)`**. Its weight in a quarter is however many of those days fall
inside it.

```
VLCC      a = 14   b = 66
Suezmax   a = 20   b = 44
```

- **`b` is the load-to-discharge window** — Frontline recognises revenue
  ratably from commencement of loading to completion of discharge. MEASURED at
  66.6 days from 17 broker fixtures (`data/voyage_cycle.md`), against the 66
  in config. Independent of anything it was fitted to.
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
17 quarters. The ordering follows voyage length: Suezmax `b` = 44 against
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

---

# The variables to check

Ordered by how much damage a wrong value does.

| # | variable | status | how it fails |
|---|---|---|---|
| 1 | **uplift 1.02 at extreme rates** | measured to 150k, applied at 475k | A 3.2x extrapolation. If capture falls at high rates, Q4 is wrong and nothing else saves it. Everything rests here. |
| 2 | **`a` = 14** | FITTED, not measured | The only curve-fit left. Measured ballast is 27.5d; using it worsens the back-test. Unresolved, not settled. |
| 3 | **Suezmax uplift 1.03** | NOT measured | Its basket is inconsistent, so the ratio cannot be computed. |
| 4 | **Suezmax kernel 20/44** | SCALED from VLCC | No Suezmax voyage splits exist. |
| 5 | **coverage % for an undisclosed quarter** | assumed 79% | Historical mean. Frontline discloses the real one each quarter. |
| 6 | **54/46 non-VLCC day split** | one quarter | From 2026Q2 actuals only. |
| 7 | **TCE-to-profit gap 173.1** | one quarter | Calibrated on 2026Q2, held flat across a changing fleet. |

**The near-term test.** Q3 2026 reports in late November and settles two
things at once: the Q3 predictions on record (`predictions/2026Q3.md`), and
Frontline's disclosed **Q4 covered rate**, which is the direct test of
variable 1 — the one the whole forecast hangs on.

**Where we disagree with the market.** Consensus Q4 EPS is $1.58 against our
$7.52. Working backwards, $1.58 implies a Q4 VLCC spot TCE near $92,000/day,
below Q3 and a fifth of what is already locked in printed weeks. The consensus
Q4 figure has not moved since before the spike began (1.40 / 1.60 / 1.58 /
1.58 / 1.58 at 90/60/30/7/0 days) while the Q3 figure rose 1.38 -> 2.27. Three
analysts cover the stock. Read that as stale rather than considered — but it
is the only independent check available, and it disagrees by 4.8x.
