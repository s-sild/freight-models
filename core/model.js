// Shared model. Mirrors core/model.py exactly — the Python side is the one with
// acceptance tests, so if these ever disagree, Python is right.

export function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  const head = lines[0].split(",");
  return lines.slice(1).map(l => {
    // naive split is fine: no quoted commas in our data, and validate.py would catch it
    const cells = l.split(",");
    const o = {};
    head.forEach((h, i) => (o[h.trim()] = (cells[i] ?? "").trim()));
    return o;
  });
}

export const num = v => {
  if (v === undefined || v === null || String(v).trim() === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
};

const meanOf = vals => {
  const v = vals.map(num).filter(x => x !== null);
  return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null;
};

// --- 1. route assessments -> company-equivalent benchmark -------------------
export function blend(row, spec) {
  const atl = meanOf(spec.atlantic.map(r => row[r]));
  if (atl === null) return null;
  let v = atl;
  if (spec.premium) {
    const p = num(row[spec.premium]);
    if (p === null) return null;
    const w = spec.premium_weight ?? 0;
    v = (1 - w) * atl + w * p;
  }
  return v * (spec.factor ?? 1);
}

// --- 2. recognition kernel --------------------------------------------------
const DAY = 86400000;

export function quarterBounds(q) {
  const y = +q.slice(0, 4), qq = +q.slice(-1);
  return [Date.UTC(y, 3 * qq - 3, 1), qq === 4 ? Date.UTC(y + 1, 0, 1) : Date.UTC(y, 3 * qq, 1)];
}

/**
 * series: [[msTimestamp, rate|null], ...] — published weeks only.
 * Returns {tce, observed}.
 *
 * `observed` is measured against every week that FEEDS the quarter, including
 * ones not yet published. Dividing by the weeks present in the series instead
 * returns ~1.0 by construction, since an unpublished week is simply absent.
 */
export function kernelQuarter(series, q, { a, b, factor = 1 }) {
  const [qs, qe] = quarterBounds(q);
  const have = new Map(series.filter(p => p[1] !== null));
  if (!have.size) return { tce: null, observed: 0 };
  const anchor = Math.max(...have.keys());

  // a week D reaches the quarter when D is in (qs - a - b, qe - a)
  const first = qs - (a + b + 7) * DAY, last = qe - a * DAY + 7 * DAY;
  const start = first + (((anchor - first) / DAY) % 7) * DAY;

  let total = 0, known = 0, acc = 0;
  for (let t = start; t <= last; t += 7 * DAY) {
    const s = t + a * DAY, e = s + b * DAY;
    const ov = Math.max(0, (Math.min(e, qe) - Math.max(s, qs)) / DAY);
    if (ov <= 0) continue;
    total += ov;
    const r = have.get(t);
    if (r !== undefined) { known += ov; acc += ov * r; }
  }
  if (!known) return { tce: null, observed: 0 };
  return { tce: (acc / known) * factor, observed: known / total };
}

// --- 3. coverage model ------------------------------------------------------
export const coverage = (contracted, covPct, k) => {
  const c = covPct > 1 ? covPct / 100 : covPct;
  return contracted * (c + (1 - c) * k);
};

export const impliedK = (contracted, covPct, actual) => {
  const c = covPct > 1 ? covPct / 100 : covPct;
  return c >= 1 ? null : (actual / contracted - c) / (1 - c);
};

// --- 4. cash flow and implied price ----------------------------------------
export class FcfModel {
  constructor(cfg) {
    this.baseFcf = cfg.base_fcf_musd;
    this.baseFps = cfg.base_fcf_per_share;
    this.rates = cfg.base_rates_kusd_day;
    this.days = cfg.spot_days_12m;
    this.shares = this.baseFcf / this.baseFps;
    this.sensitivity = (cfg.fcf_at_plus_30_musd - this.baseFcf) / 0.3;
    const lead = Object.keys(this.rates)[0];
    const r0 = this.rates[lead];
    this.a = r0 * (1 - this.baseFcf / this.sensitivity);
    this.b = (r0 * this.shares) / this.sensitivity;
  }
  fcf(rates) {
    const d = Object.keys(this.rates)
      .reduce((s, k) => s + this.days[k] * (rates[k] - this.rates[k]), 0) / 1000;
    return this.baseFcf + d;
  }
  fcfPerShare(rates) { return this.fcf(rates) / this.shares; }
  price(rates, y) { return this.fcfPerShare(rates) / y; }
  impliedRate(price, y) { return this.a + this.b * price * y; }
  impliedYieldOnBase(price) { return this.baseFps / price; }
}

// --- formatting -------------------------------------------------------------
export const fmt = {
  usd: v => v === null || v === undefined ? "—" : "$" + Math.round(v).toLocaleString("en-US"),
  usd2: v => v === null || v === undefined ? "—" : "$" + v.toFixed(2),
  k: v => v === null || v === undefined ? "—" : Math.round(v / 1000).toLocaleString("en-US") + "k",
  pct: (v, d = 1) => v === null || v === undefined ? "—" : (v * 100).toFixed(d) + "%",
  signed: (v, d = 1) => v === null || v === undefined ? "—"
    : (v >= 0 ? "+" : "") + (v * 100).toFixed(d) + "%",
  date: t => new Date(t).toISOString().slice(0, 10),
};
