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

    No benchmark-to-owner conversion happens here. That uplift belongs on the
    observed weeks at series construction - see uplift() - because a forecast
    anchor the user types is already an owner-level rate and marking it up
    again double-counts. `factor` stays 1.0 and survives only so a caller with
    a genuine per-kernel scale could still pass one.
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

        Returns (tce, share_locked). The denominator is every week that FEEDS
        the quarter and can still be published — otherwise the share is near
        1.0 by construction, because a week with no data is simply absent from
        the series.

        A gap BEFORE the anchor is not a pending week. The Baltic does not
        publish over UK holidays — Good Friday, Christmas, New Year — so 14 of
        the 250 slots in five years never carried a print and never will.
        Counting them as awaiting publication pushed every Q1 and Q2 reading
        several points low. They are dropped from the denominator here, which
        is a fix to the model; the series itself is left exactly as reported,
        with no invented rows.
        """
        if not series:
            return None, 0.0
        anchor = max(series)
        weeks = self.feed_weeks(anchor, q)
        w = self.weights(weeks, q)
        w = [wi if (d > anchor or d in series) else 0.0 for wi, d in zip(w, weeks)]
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

def uplift(series, f):
    """
    Scale a benchmark series {date: rate} to owner-realised terms. OBSERVED
    weeks only: a forecast anchor the user types is already owner-level, and
    marking it up again was the 140 -> 147 bug.
    """
    return {d: (None if v is None else v * f) for d, v in series.items()}


def fixed_share(asof, q, phi):
    """
    Share of quarter `q` whose rate is already fixed, as of `asof`.

        fixed = elapsed + phi x (1 - elapsed)

    Elapsed days are fixed by definition - the voyages happened. Of the days
    remaining, phi is already on subs. phi is solved from Frontline's own 18
    disclosed coverage figures.

    This replaced a flat idle haircut on the kernel's fill. The haircut matched
    the disclosures at the one date they are published and changed nothing
    about the SHAPE of the curve: the kernel still reached ~99% by day 57 and
    71% by day 19, and the rate blend still used those weights. Scaling a wrong
    curve by a constant leaves it wrong everywhere except the calibration
    point, and leaves the forecast untouched - which was the whole problem.

    This form is right at both ends: it reaches 1.0 at quarter end, where every
    day has happened, and it rises slowly early.
    """
    qs, qe = quarter_bounds(q)
    if asof <= qs:
        return 0.0
    if asof >= qe:
        return 1.0
    elapsed = (asof - qs).days / (qe - qs).days
    return elapsed + phi * (1 - elapsed)


def quarter_rate(printed, forecast, q, kernel, phi, asof):
    """
    A quarter's TCE, blended by how much of it is actually FIXED rather than by
    how many Baltic weeks happen to have printed.

        rate = fixed x (rate over printed weeks) + (1 - fixed) x (rate over the curve)

    The kernel still decides WHICH weeks reach the quarter and with what
    weight. What it no longer decides is how much of the quarter is settled -
    it filled far too fast, weighting a quarter 71% to printed weeks on day 19
    when the company reports ~85% fixed only by day 57.

    A completed quarter has fixed = 1.0, so the back-test is untouched.
    """
    pr, _ = kernel.quarter(printed, q)
    s = fixed_share(asof, q, phi)
    if not forecast:
        return pr
    anchor = max(printed) if printed else max(forecast)
    weeks = kernel.feed_weeks(anchor, q)
    w = kernel.weights(weeks, q)
    num = den = 0.0
    for wi, d in zip(w, weeks):
        if wi <= 0 or d <= anchor:
            continue
        r = forecast.get(d)
        if r is not None:
            num += wi * r
            den += wi
    cr = (num / den * kernel.factor) if den else None
    if pr is None:
        return cr
    if cr is None:
        return pr
    return s * pr + (1 - s) * cr


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
