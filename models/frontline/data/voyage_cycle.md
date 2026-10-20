# VLCC voyage cycle

Measured 2026-10-20 from `voyage_splits.csv` (17 broker fixtures, 11 operators,
reported 2026-09-03 to 2026-10-19) plus Frontline's own ballast-day disclosures.

## Round voyage, from the fixture list

| route | n | rv_days | ballast % | load-to-discharge |
|---|---|---|---|---|
| Brazil/China | 10 | 85.1 | 38.2% | 52.3d |
| USG/Far East | 7 | 116.6 | 20.9% | 92.1d |
| MEG/China | — | 45.0 | 46.7% | 24.0d |

MEG is assumed, not measured — no MEG fixtures in the sample.

Blended at the spot-blend weights (0.88 Atlantic / 0.12 MEG, Atlantic split
50/50 Brazil/USG to match the equal TD15/TD22 weighting):

- round-voyage cycle **94.1 days**
- of which ballast **31.6%** = 29.7 days
- load-to-discharge **66.6 days**

That last figure is an independent confirmation of `kernel.vlcc.b = 66`, from
data never used to fit it.

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
- The MEG leg is assumed throughout.
- Suezmax and Aframax have no fixture data at all; their caps are derived from
  the coverage disclosures alone.
