"""
Acceptance tests for the port.

These are not unit tests of arithmetic. They are the specific numbers the
Excel model produced and that we argued about and verified over two weeks.
If the port does not reproduce them, the port is wrong.
"""
import sys, os, json
from datetime import datetime, date as dt, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))
from model import (read_csv, num, blend, Kernel, coverage, implied_k,
                   covered_share, uplift, FcfModel, mean_of)
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

def check_true(label, cond):
    """A structural assertion: holds whatever week it is run in. Prints 1/0."""
    return check(label, 1.0 if cond else 0.0, 1.0, 0.0)


# ---- series construction -------------------------------------------------
def series(seg):
    spec = CFG["blend"][seg]
    out = {}
    for r in baltic:
        v = blend(r, spec)
        if v is not None:
            out[datetime.strptime(r["week_ending"], "%Y-%m-%d").date()] = v
    return out

V, S = series("vlcc"), series("smax")          # raw Baltic benchmark

# Owner-realised terms, applied HERE and not in the kernel. A forecast anchor
# the user types is already owner-level; marking it up again turned the base
# case's 140 into 147. See config realised_uplift.
UP = CFG["realised_uplift"]
VU, SU = uplift(V, UP["vlcc"]), uplift(S, UP["smax"])

# Pinned to the DATE, not to max(V). These were `max(V)` once, which quietly
# re-aimed at whatever the newest week happened to be while the label still
# said 2026-10-09 — so every Friday they failed looking like a data error.
# A checkpoint is only a checkpoint if it keeps measuring the same thing.
WK41 = datetime.strptime("2026-10-09", "%Y-%m-%d").date()
check("FL-equivalent VLCC, week ending 2026-10-09", V[WK41], 785821.92, 1.0, "$/day")
check("FL-equivalent Suezmax, week ending 2026-10-09", S[WK41], 566600.0, 1.0, "$/day")


# ---- kernel --------------------------------------------------------------
kv = Kernel(**{k: CFG["kernel"]["vlcc"][k] for k in ("a", "b")})
ks = Kernel(**{k: CFG["kernel"]["smax"][k] for k in ("a", "b")})

tce, obs = kv.quarter(VU, "2026Q3")

# These moved on 2026-10-16 because an INPUT changed, not the model: the week
# ending 2026-08-14 was interpolated from its neighbours (its Baltic report was
# never retrieved), and that week feeds 16 days of Q3. Against the Excel's
# figures of 156,665 / 96,253, which were computed with the gap left open.
# Only ever re-pin these when the inputs deliberately change - otherwise the
# tests stop catching anything.
check("Kernel VLCC 2026Q3", tce, 158186, 400, "$/day")
check("Kernel VLCC 2026Q3 locked share is 1.0 (quarter fully fed)", obs, 1.0, 0.001)

# The locked share must be measured against every week that FEEDS a quarter,
# published or not. Count only the weeks present in the file and an unpublished
# week is simply absent, so the share reads ~1.0 whatever the truth — that bug
# reported Q4-26 as 94% locked against a real 62%.
#
# Asserted structurally, not pinned: a pinned share is a snapshot of a quantity
# that moves every Friday by design, and re-pinning it weekly trains you to
# ignore the suite. Removing the newest published week must never RAISE a
# locked share and must LOWER at least one. Under the old bug it did neither:
# numerator and denominator shrank together and the share stayed ~1.0.
VU_less = {d: v for d, v in VU.items() if d != max(VU)}
pairs = [(q, kv.quarter(VU, q)[1], kv.quarter(VU_less, q)[1]) for q in CFG["quarters_12m"]]
check_true("Dropping the newest week never raises a locked share",
           all(less <= full + 1e-12 for _, full, less in pairs))
check_true("Dropping the newest week lowers at least one locked share",
           any(less < full - 1e-9 for _, full, less in pairs))

# Far enough out that no published week can reach it, computed from the data
# rather than hardcoded — "2027Q2" stops being a future quarter in Feb 2027.
far = max(V).year + 2
check("A quarter with no feed weeks yet reports zero locked",
      kv.quarter(VU, f"{far}Q2")[1], 0.0, 0.0001)


# ---- covered share -------------------------------------------------------
# The panel's one number. covered = elapsed + phi * (1 - elapsed), phi solved
# from all 18 disclosures. Structural, so it does not need re-pinning.
PHI = CFG["coverage_estimate"]["phi"]
check("phi is the full-sample mean of the 18 disclosures", PHI, 0.447, 0.001)
check("Covered at quarter start equals phi", covered_share(dt(2026,10,1), "2026Q4", PHI), PHI, 1e-9)
check("Covered on the last day is ~1", covered_share(dt(2026,12,31), "2026Q4", PHI), 1.0, 0.012)
check_true("Covered is undefined before the quarter starts",
           covered_share(dt(2026,9,30), "2026Q4", PHI) is None)
check_true("Covered rises every day through the quarter",
           all(covered_share(dt(2026,10,1)+timedelta(days=i), "2026Q4", PHI)
               < covered_share(dt(2026,10,1)+timedelta(days=i+1), "2026Q4", PHI)
               for i in range(90)))
# Reproduces the disclosures it was fitted to: mean error across all 18 is zero
# by construction, so the test is that the SPREAD is what we measured.
errs = []
for r in quarterly:
    y, n = (int(r["quarter"][:4]) + 1, 1) if r["quarter"][-1] == "4" \
           else (int(r["quarter"][:4]), int(r["quarter"][-1]) + 1)
    c = covered_share(dt.fromisoformat(r["report_date"]), f"{y}Q{n}", PHI)
    errs.append(c * 100 - int(r["vlcc_next_cov_pct"]))
check("Covered vs the 18 disclosures, mean error", st.mean(errs), 0.0, 0.3, "pts")
check("Covered vs the 18 disclosures, mean abs error", st.mean([abs(e) for e in errs]), 3.85, 0.05, "pts")


# ---- the uplift is not applied twice -------------------------------------
# Set every unpublished week to the slide's own base rate and the far quarters
# must read BACK that rate. They read 147,000 against 140 while the uplift sat
# inside the kernel, because a typed anchor is already an owner-level rate.
# This is the regression guard for that bug.
base_v = CFG["fcf"]["base_rates_kusd_day"]["vlcc"] * 1000
fwd = dict(VU)
_d = max(VU) + timedelta(days=7)
for _ in range(80):
    fwd[_d] = base_v
    _d += timedelta(days=7)
far_q = CFG["quarters_12m"][-1]          # far enough that no published week feeds it
check(f"Base-case anchor reads back unchanged in {far_q}",
      kv.quarter(fwd, far_q)[0], base_v, 1.0, "$/day")
check_true("An observed week IS uplifted",
           abs(VU[max(VU)] / V[max(V)] - CFG["realised_uplift"]["vlcc"]) < 1e-12)

tce_s, _ = ks.quarter(SU, "2026Q3")
check("Kernel Suezmax 2026Q3", tce_s, 97732, 400, "$/day")


# ---- kernel back-test ----------------------------------------------------
# These are the errors we measured against reported TCEs.
BACKTEST = {
    "2025Q3": (37141, 35401), "2025Q4": (72648, 59545),
    "2026Q1": (102519, 71583), "2026Q2": (161589, 118664),
}
for q, (wantv, wants) in BACKTEST.items():
    gv, _ = kv.quarter(VU, q)
    gs, _ = ks.quarter(SU, q)
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
