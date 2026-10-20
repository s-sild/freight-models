"""
How a quarter actually fills, from disclosed data only.

Reconciles each quarter three ways:

    covered days      = actual spot days x coverage % stated at the report
    earned covered    = covered days x the contracted rate stated at the report
    earned total      = actual spot days x the realised TCE later reported
    earned uncovered  = earned total - earned covered          <- the residual

The number the table isolates is the LAST column: how far the realised TCE
landed below the rate that was already contracted when the report was
published. If a quarter can be 82% covered at $181,700 and still print
$152,731, then treating the known rate as the quarter's answer overstates it.

Read `k` with care. Uncovered earnings are a residual, so they absorb every
inconsistency in the inputs - above all that the coverage % was stated against
Frontline's ESTIMATE of the quarter's spot days, while the day count here is
the actual. The gap column is the robust one: it uses two disclosed figures
and no arithmetic of ours.

    python3 model/quarter_fill.py
"""
import csv, os, statistics as st

ROOT = os.path.join(os.path.dirname(__file__), "..", "models", "frontline")
rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "quarter_fill.csv"))))
n = lambda r, k: float(r[k])

print(f"{'quarter':<9}{'segment':<9}{'cov':>5}{'days':>7}{'contracted':>12}"
      f"{'uncovered':>11}{'k':>6}{'realised':>10}{'gap':>7}")
print("-" * 76)
gaps, ks = {}, {}
for r in rows:
    unc = n(r, "uncovered_days")
    ku = n(r, "earned_uncovered_kusd") * 1000 / unc if unc else float("nan")
    k = ku / n(r, "contracted_rate")
    gap = n(r, "realised_tce") / n(r, "contracted_rate") - 1
    gaps.setdefault(r["segment"], []).append(gap)
    ks.setdefault(r["segment"], []).append(k)
    print(f"{r['quarter']:<9}{r['segment']:<9}{n(r,'cov_pct_at_report'):>4.0f}%"
          f"{n(r,'actual_spot_days'):>7.0f}{n(r,'contracted_rate'):>12,.0f}"
          f"{ku:>11,.0f}{k:>6.0%}{n(r,'realised_tce'):>10,.0f}{gap:>7.0%}")

print(f"\n{'segment':<10}{'n':>3}{'mean gap':>10}{'range':>16}{'mean k':>9}{'k range':>16}")
for seg in ks:
    g, kk = gaps[seg], ks[seg]
    print(f"{seg:<10}{len(g):>3}{st.mean(g):>9.0%}  {min(g):>5.0%} to {max(g):>4.0%}"
          f"{st.mean(kk):>9.0%}  {min(kk):>5.0%} to {max(kk):>4.0%}")

allg = [x for v in gaps.values() for x in v]
print(f"\nacross all {len(allg)} readings: realised landed {st.mean(allg):.0%} below the "
      f"contracted rate on average,\nrange {min(allg):.0%} to {max(allg):.0%}. "
      f"Coverage at the report ran "
      f"{min(n(r,'cov_pct_at_report') for r in rows):.0f}-"
      f"{max(n(r,'cov_pct_at_report') for r in rows):.0f}%.")
