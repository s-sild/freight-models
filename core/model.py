"""
Freight-rate -> earnings model core.

Nothing here is Frontline-specific except the defaults loaded from a model's
config.json. The four pieces are:

  blend()      weekly route assessments -> one company-equivalent benchmark
  kernel()     weekly benchmark -> quarterly recognised TCE, via a ballast/laden lag
  coverage()   reported contracted rate + % covered -> full-quarter outcome
  FcfModel     rate -> free cash flow -> implied price, and its inverse

Every number this produces is traceable to a CSV row with a source column.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
import csv, json, statistics as st


# --------------------------------------------------------------------------
# data loading
# --------------------------------------------------------------------------

def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def num(v):
    """CSV cell -> float or None. Blank means 'not disclosed', never zero."""
    if v is None:
        return None
    v = str(v).strip()
    if v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def mean_of(vals):
    vals = [v for v in (num(x) for x in vals) if v is not None]
    return sum(vals) / len(vals) if vals else None


# --------------------------------------------------------------------------
# 1. route assessments -> company-equivalent benchmark
# --------------------------------------------------------------------------

def blend(row, spec):
    """
    spec = {"atlantic": [...routes...], "premium": "TD3C", "premium_weight": 0.12,
            "factor": 1.0}

    The premium route carries its own weight because a company's exposure to it
    differs from an equal-weighted index. With no premium route, this is just the
    average of the listed routes times the factor.
    """
    atl = mean_of([row.get(r) for r in spec["atlantic"]])
    if atl is None:
        return None
    prem_route = spec.get("premium")
    if prem_route:
        p = num(row.get(prem_route))
        if p is None:
            return None
        w = spec.get("premium_weight", 0.0)
        atl = (1 - w) * atl + w * p
    return atl * spec.get("factor", 1.0)


# --------------------------------------------------------------------------
# 2. recognition kernel
# --------------------------------------------------------------------------

def quarter_bounds(q):
    """'2026Q4' -> (date(2026,10,1), date(2027,1,1)) — end is exclusive."""
    y, qq = int(q[:4]), int(q[-1])
    start = date(y, 3 * qq - 2, 1)
    end = date(y + 1, 1, 1) if qq == 4 else date(y, 3 * qq + 1, 1)
    return start, end


@dataclass
class Kernel:
    """
    A cargo fixed in the week ending D ballasts for `a` days earning nothing,
    then earns ratably across `b` laden days. So week D's rate is recognised
    over [D+a, D+a+b). A quarter's TCE is the weighted mean of weekly rates,
    weighted by how many earning-days land inside it.

    `factor` converts the market benchmark to what this owner actually reports.
    """
    a: int
    b: int
    factor: float = 1.0

    def weights(self, weeks, q):
        qs, qe = quarter_bounds(q)
        out = []
        for d in weeks:
            s = d + timedelta(days=self.a)
            e = s + timedelta(days=self.b)
            overlap = (min(e, qe) - max(s, qs)).days
            out.append(max(0, overlap))
        return out

    def feed_weeks(self, anchor, q):
        """
        Every weekly date whose earning window can touch quarter q, published or
        not. A week D earns across [D+a, D+a+b), so it reaches q when
        D is in (qs - a - b, qe - a). `anchor` fixes the day of week.
        """
        qs, qe = quarter_bounds(q)
        first = qs - timedelta(days=self.a + self.b + 7)
        last = qe - timedelta(days=self.a) + timedelta(days=7)
        shift = (anchor - first).days % 7
        d, out = first + timedelta(days=shift), []
        while d <= last:
            out.append(d)
            d += timedelta(days=7)
        return out

    def quarter(self, series, q):
        """
        series = {date: rate}, published weeks only.

        Returns (tce, share_observed). The denominator is every week that FEEDS
        the quarter, including ones not yet published — otherwise the share is
        near 1.0 by construction, because a week with no data is simply absent
        from the series.
        """
        if not series:
            return None, 0.0
        anchor = max(series)
        weeks = self.feed_weeks(anchor, q)
        w = self.weights(weeks, q)
        tot = sum(w)
        if tot == 0:
            return None, 0.0
        known = [(wi, series[d]) for wi, d in zip(w, weeks)
                 if wi > 0 and series.get(d) is not None]
        kw = sum(wi for wi, _ in known)
        if kw == 0:
            return None, 0.0
        return sum(wi * r for wi, r in known) / kw * self.factor, kw / tot


# --------------------------------------------------------------------------
# 3. coverage model
# --------------------------------------------------------------------------

def coverage(contracted, covered_pct, k):
    """
    At the report date `covered_pct` of the quarter's days are contracted at
    `contracted`. The uncovered remainder earns k x that rate.
    k is calibrated from history, not assumed — see implied_k().
    """
    c = covered_pct / 100.0 if covered_pct > 1 else covered_pct
    return contracted * (c + (1 - c) * k)


def implied_k(contracted, covered_pct, actual):
    """Invert coverage() against what the next quarter actually printed."""
    c = covered_pct / 100.0 if covered_pct > 1 else covered_pct
    if c >= 1:
        return None
    return ((actual / contracted) - c) / (1 - c)


# --------------------------------------------------------------------------
# 4. cash flow and implied price
# --------------------------------------------------------------------------

@dataclass
class FcfModel:
    """
    Built from the company's own published cash-generation sensitivity:
    a base-case FCF at a stated set of rates, plus FCF at rates +30%.
    That pins a linear relation between day-rates and free cash flow.
    """
    base_fcf: float          # $m
    base_fcf_per_share: float
    fcf_at_plus_30: float    # $m
    base_rates: dict         # {segment: $k/day}
    spot_days: dict          # {segment: days over the 12m window}

    def __post_init__(self):
        self.shares = self.base_fcf / self.base_fcf_per_share
        self.sensitivity = (self.fcf_at_plus_30 - self.base_fcf) / 0.30
        lead = next(iter(self.base_rates))
        self._lead = lead
        r0 = self.base_rates[lead]
        self.a = r0 * (1 - self.base_fcf / self.sensitivity)
        self.b = r0 * self.shares / self.sensitivity

    def fcf(self, rates):
        """rates = {segment: $k/day}. Returns $m."""
        delta = sum(self.spot_days[s] * (rates[s] - self.base_rates[s])
                    for s in self.base_rates) / 1000.0
        return self.base_fcf + delta

    def fcf_per_share(self, rates):
        return self.fcf(rates) / self.shares

    def price(self, rates, required_yield):
        return self.fcf_per_share(rates) / required_yield

    def implied_rate(self, price, required_yield):
        """Inverse: what flat lead-segment rate does this price imply?"""
        return self.a + self.b * price * required_yield

    def implied_yield_on_base(self, price):
        """The market's cap rate on the company's own published base case."""
        return self.base_fcf_per_share / price


def load_config(path):
    with open(path) as f:
        return json.load(f)
