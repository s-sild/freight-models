"""
Acceptance tests for the port.

These are not unit tests of arithmetic. They are the specific numbers the
Excel model produced and that we argued about and verified over two weeks.
If the port does not reproduce them, the port is wrong.
"""
import sys, os, json
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))
from model import (read_csv, num, blend, Kernel, coverage, implied_k,
                   FcfModel, mean_of)
import statistics as st

ROOT = os.path.join(os.path.dirname(__file__), "..", "models", "frontline")
CFG = json.load(open(os.path.join(ROOT, "config.json")))
D = lambda n: os.path.join(ROOT, "data", n)

baltic = read_csv(D("baltic_weekly.csv"))
quarterly = read_csv(D("fro_quarterly.csv"))

results = []
def check(label, got, want, tol, unit=""):
    ok = got is not None and abs(got - want) <= tol
    results.append((ok, label, got, want, unit))
    return ok


# ---- series construction -------------------------------------------------
def series(seg):
    spec = CFG["blend"][seg]
    out = {}
    for r in baltic:
        v = blend(r, spec)
        if v is not None:
            out[datetime.strptime(r["week_ending"], "%Y-%m-%d").date()] = v
    return out

V, S = series("vlcc"), series("smax")
wk41 = max(V)

check("FL-equivalent VLCC, week ending 2026-10-09", V[wk41], 785821.92, 1.0, "$/day")
check("FL-equivalent Suezmax, week ending 2026-10-09", S[wk41], 566600.0, 1.0, "$/day")


# ---- kernel --------------------------------------------------------------
kv = Kernel(**{k: CFG["kernel"]["vlcc"][k] for k in ("a", "b", "factor")})
ks = Kernel(**{k: CFG["kernel"]["smax"][k] for k in ("a", "b", "factor")})

tce, obs = kv.quarter(V, "2026Q3")
check("Kernel VLCC 2026Q3", tce, 156665, 400, "$/day")
check("Kernel VLCC 2026Q3 share observed", obs, 1.0, 0.001)

tce_s, _ = ks.quarter(S, "2026Q3")
check("Kernel Suezmax 2026Q3", tce_s, 96253, 400, "$/day")


# ---- kernel back-test ----------------------------------------------------
# These are the errors we measured against reported TCEs.
BACKTEST = {
    "2025Q3": (37141, 35401), "2025Q4": (72648, 59545),
    "2026Q1": (102519, 71583), "2026Q2": (161589, 118664),
}
for q, (wantv, wants) in BACKTEST.items():
    gv, _ = kv.quarter(V, q)
    gs, _ = ks.quarter(S, q)
    check(f"Kernel back-test VLCC {q}", gv, wantv, max(600, wantv * 0.01), "$/day")
    check(f"Kernel back-test Suezmax {q}", gs, wants, max(600, wants * 0.01), "$/day")


# ---- coverage model ------------------------------------------------------
k = CFG["coverage"]["k"]
check("Coverage model, 2026Q3 VLCC (156,900 @ 86%)",
      coverage(156900, 86, k), 140865, 50, "$/day")

# implied k across every quarter where the next quarter's actual is known
qs = [r for r in quarterly if r["quarter"]]
ks_list = []
for i in range(len(qs) - 1):
    c = num(qs[i]["vlcc_next_contracted"]); cov = num(qs[i]["vlcc_next_cov_pct"])
    act = num(qs[i + 1]["vlcc_spot_tce"])
    if None not in (c, cov, act):
        ks_list.append(implied_k(c, cov, act))
check("Implied k, number of quarters", float(len(ks_list)), 17.0, 0.5)
check("Implied k, median", st.median(ks_list), 0.275, 0.005)
check("Implied k, mean", st.mean(ks_list), 0.297, 0.005)


# ---- cash flow and implied yield ----------------------------------------
f = CFG["fcf"]
m = FcfModel(f["base_fcf_musd"], f["base_fcf_per_share"], f["fcf_at_plus_30_musd"],
             f["base_rates_kusd_day"], f["spot_days_12m"])

check("Shares outstanding", m.shares, 222.705, 0.01, "m")
rebuilt = sum(m.spot_days[s] * m.base_rates[s] for s in m.base_rates) / 1000.0
check("Rebuilt sensitivity equals published sensitivity", rebuilt, m.sensitivity, 1.0, "$m")
check("Base case reproduces published FCF/share",
      m.fcf_per_share(f["base_rates_kusd_day"]), 10.35, 0.01, "$")

check("Implied yield on base case at $41.40 (28 Aug 2026)",
      m.implied_yield_on_base(41.40), 0.250, 0.001)
check("Implied 12m VLCC at $59.06 @ 24%", m.implied_rate(59.06, 0.24), 185.2, 0.2, "$k/day")
check("Implied 12m VLCC at $59.06 @ 20%", m.implied_rate(59.06, 0.20), 157.3, 0.2, "$k/day")

# 1-yr T/C basis, 15 Oct 2026
tc = {"vlcc": 225.0, "smax": 165.0, "lr2": 100.0}
check("FCF/share at 1-yr T/C rates", m.fcf_per_share(tc), 17.20, 0.02, "$")
check("Implied yield at $55.87 on T/C basis", m.fcf_per_share(tc) / 55.87, 0.308, 0.001)


# ---- report --------------------------------------------------------------
w = max(len(r[1]) for r in results)
fails = 0
for ok, label, got, want, unit in results:
    mark = "PASS" if ok else "FAIL"
    if not ok:
        fails += 1
    g = f"{got:,.4f}" if isinstance(got, float) else str(got)
    print(f"[{mark}] {label:<{w}}  got {g:>14}  want {want:>12,}  {unit}")

print(f"\n{len(results) - fails}/{len(results)} passed")
sys.exit(1 if fails else 0)
