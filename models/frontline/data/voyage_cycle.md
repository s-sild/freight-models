# VLCC voyage cycle

Measured 2026-10-20 from `voyage_splits.csv` (17 broker fixtures, 11 operators,
reported 2026-09-03 to 2026-10-19) plus Frontline's own ballast-day disclosures.

## Round voyage, from the fixture list

**Corrected 2026-11-13.** The ballast/laden/port percentages are a share of
`actual_days`, not `rv_days`. The source carries both and they are not the
same voyage: across 21 fixtures `rv_days − actual_days` runs from −7 to +45
against idle time under 1.5 days, so `rv` is a modelled round trip back to the
load area and `actual` is the leg in hand. The original table multiplied the
percentages by `rv_days` and overstated every figure below.

The source proves the base itself: it gives idle time twice, as days and as a
percentage, and the implied total is `actual_days` every time — 1.00d = 1.8%
gives 55.6 against 55 actual; 1.48d = 2.7% gives 54.8 against 55; 0.79d = 1.6%
gives 49.4 against 48; 0.26d = 0.4% gives 65.0 against 63.

**MEG/East is now measured.** Frontline's own fixture list carries routes, and
five of its voyages are East of Suez (3 RSea/Korea, 1 AG/Korea, 1 AG/Spore).
The leg is no longer an assumption.

| route | n | actual_days | ballast % | load-to-discharge |
|---|---|---|---|---|
| Brazil/China | 10 | 81.9 | 38.2% | 50.0d |
| USG/Far East | 7 | 90.0 | 21.1% | 69.4d |
| MEG/East | 5 | 49.8 | 39.0% | 29.9d |

Measured MEG runs longer and lighter on ballast than the 45.0d / 46.7% / 24.0d
previously assumed. Where a fixture appears at two vintages the later one is
kept — Gander, Alta and Beauly were each carried twice.

Blended at the spot-blend weights (0.88 Atlantic / 0.12 MEG, Atlantic split
50/50 Brazil/USG to match the equal TD15/TD22 weighting):

- load-to-discharge **56.3 days** (was stated as 66.6)

**This is no longer a confirmation of `kernel.vlcc.b = 66`.** It reads 15%
below it. `b` was not derived from this file, so the kernel is unchanged, but
it now rests on its curve fit alone. Q4 2026 is insensitive — at 88% fed, a
shorter window raises the quarter (b=66 gives $491,905, b=56 gives $517,621),
so the figure in the model is the conservative one.

## Fixture to fixture

The coverage cap (0.814, see below) implies unfixed time on top of the voyage:

| | days |
|---|---|
| contracted ballast | 29.7 |
| laden (load-to-discharge) | 66.4 |
| **contracted voyage** | **96.1** |
| unfixed, awaiting next cargo | 22.0 |
| **fixture to fixture** | **118.1** |

96.1 / 118.1 = 0.814.

## Three checks

None of these were used to construct the cap.

| | predicted | disclosed |
|---|---|---|
| contracted ballast, % of all spot days | 25.2% | 23.6% (16 quarters) |
| voyages per ship per quarter | 0.77 | 0.79 |
| ships ballasting under contract, 2026Q2 | 6.1 | 6.4 |

Fleet decomposition, 2026Q2 (24.3 VLCC spot vessel-equivalents):
13.7 laden, 6.1 ballasting toward a fixed cargo, 4.5 unfixed.

## The cap itself

`c_inf` = Frontline's disclosed coverage % divided by the kernel's cumulative
weight at the same date, over 17 quarters:

| segment | mean | median | sd |
|---|---|---|---|
| VLCC | 0.814 | 0.804 | 0.051 |
| Suezmax | 0.763 | 0.766 | 0.043 |
| Aframax | 0.666 | 0.677 | 0.054 |

NOT IMPLEMENTED as of 2026-10-20. It is a coverage figure and belongs on the
displayed "% covered" number, not in the rate blend — see `notes.md`.

## Caveats

- 17 fixtures from one month at a market peak, with unusually long Atlantic
  ballast legs. The cycle is likely high against a multi-year average: the
  disclosed-ballast route gives 87.2d (median 86.7, range 80-96) against 94.1
  here.
- The MEG leg is now measured (n=5) rather than assumed.
- Suezmax and Aframax have no fixture data at all; their caps are derived from
  the coverage disclosures alone.
