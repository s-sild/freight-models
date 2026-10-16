// Minimal SVG line chart with crosshair + tooltip. No dependencies, so it
// works offline and there is no CDN version to rot.
//
// Palette slots 1 and 2 from the reference palette, validated in both modes:
//   light #2a78d6 / #eb6834   dark #3987e5 / #d95926

const NS = "http://www.w3.org/2000/svg";
const el = (n, a = {}) => {
  const e = document.createElementNS(NS, n);
  for (const [k, v] of Object.entries(a)) e.setAttribute(k, v);
  return e;
};

/**
 * mount(node, {series, yLabel, log, fmtY, fmtX})
 * series: [{name, color, points: [[x(ms), y|null], ...]}]
 */
export function lineChart(node, opts) {
  const { series: rawSeries, log = false, fmtY = v => v, fmtX = t => new Date(t).toISOString().slice(0, 10) } = opts;
  const W = node.clientWidth || 640, H = opts.height || 220;
  const M = { t: 10, r: 12, b: 24, l: 56 };
  const iw = W - M.l - M.r, ih = H - M.t - M.b;

    // a log axis cannot show the non-positive TCEs of early 2022 — leave them as gaps, not a floor
  const series = log
    ? rawSeries.map(s => ({ ...s, points: s.points.map(([x, y]) => [x, y !== null && y > 0 ? y : null]) }))
    : rawSeries;
  const pts = series.flatMap(s => s.points.filter(p => p[1] !== null));
  if (!pts.length) { node.textContent = "no data"; return; }
  const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs);
  let y0 = Math.min(...ys), y1 = Math.max(...ys);
  if (log) {
    // snap the axis out to 1/2/5 steps so the data always sits inside the
    // labelled gridlines — a line above the top gridline has no scale to read
    const step = (v, up) => {
      const e = Math.floor(Math.log10(v));
      const cands = [1, 2, 5, 10].map(m => m * 10 ** e);
      return up ? cands.find(c => c >= v) : [...cands].reverse().find(c => c <= v);
    };
    y0 = step(Math.max(y0, 1), false);
    y1 = step(y1, true);
  } else {
    y0 = Math.min(y0, 0) === 0 ? 0 : y0 * 0.9;
    y1 *= 1.05;
  }

  const sx = t => M.l + ((t - x0) / (x1 - x0 || 1)) * iw;
  const sy = v => {
    if (!log) return M.t + ih - ((v - y0) / (y1 - y0 || 1)) * ih;
    const l0 = Math.log10(y0), l1 = Math.log10(y1);
    return M.t + ih - ((Math.log10(Math.max(v, y0)) - l0) / (l1 - l0 || 1)) * ih;
  };

  const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", height: H, role: "img" });
  svg.setAttribute("aria-label", opts.ariaLabel || "");

  // y gridlines — recessive
  // Log ticks are generated across the actual range, not picked from a fixed list —
  // a hardcoded list silently drops the top tick when the data outruns it, leaving
  // lines above the highest labelled gridline.
  let ticks;
  if (log) {
    ticks = [];
    for (let e = Math.floor(Math.log10(y0)); e <= Math.ceil(Math.log10(y1)); e++)
      for (const mult of [1, 2, 5]) {
        const t = mult * 10 ** e;
        if (t >= y0 && t <= y1) ticks.push(t);
      }
    while (ticks.length > 8) ticks = ticks.filter((_, i) => i % 2 === 0);
  } else {
    ticks = Array.from({ length: 4 }, (_, i) => y0 + ((y1 - y0) * (i + 1)) / 4);
  }
  for (const v of ticks) {
    const y = sy(v);
    svg.append(el("line", { x1: M.l, x2: W - M.r, y1: y, y2: y, class: "viz-grid" }));
    const t = el("text", { x: M.l - 8, y: y + 4, class: "viz-tick", "text-anchor": "end" });
    t.textContent = fmtY(v);
    svg.append(t);
  }
  // x ends only — no clutter
  for (const [t, anchor] of [[x0, "start"], [x1, "end"]]) {
    const n = el("text", { x: sx(t), y: H - 6, class: "viz-tick", "text-anchor": anchor });
    n.textContent = fmtX(t);
    svg.append(n);
  }

  for (const s of series) {
    const segs = [];
    let cur = [];
    for (const [x, y] of s.points) {
      if (y === null) { if (cur.length) segs.push(cur); cur = []; }
      else cur.push(`${sx(x).toFixed(1)},${sy(y).toFixed(1)}`);
    }
    if (cur.length) segs.push(cur);
    for (const seg of segs) {
      svg.append(el("polyline", { points: seg.join(" "), fill: "none", stroke: s.color,
        "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }));
    }
  }

  // crosshair + tooltip
  const cross = el("line", { y1: M.t, y2: M.t + ih, class: "viz-cross", visibility: "hidden" });
  svg.append(cross);
  const dots = series.map(s => {
    const d = el("circle", { r: 4, fill: s.color, stroke: "var(--surface-1)",
      "stroke-width": 2, visibility: "hidden" });
    svg.append(d); return d;
  });
  node.replaceChildren(svg);

  const tip = document.createElement("div");
  tip.className = "viz-tip"; tip.hidden = true;
  node.style.position = "relative";
  node.append(tip);

  const allX = [...new Set(series.flatMap(s => s.points.map(p => p[0])))].sort((a, b) => a - b);
  svg.addEventListener("pointermove", ev => {
    const r = svg.getBoundingClientRect();
    const px = ((ev.clientX - r.left) / r.width) * W;
    const t = x0 + ((px - M.l) / iw) * (x1 - x0);
    const nearest = allX.reduce((a, b) => (Math.abs(b - t) < Math.abs(a - t) ? b : a));
    cross.setAttribute("x1", sx(nearest)); cross.setAttribute("x2", sx(nearest));
    cross.setAttribute("visibility", "visible");
    let rows = `<div class="viz-tip-h">${fmtX(nearest)}</div>`;
    series.forEach((s, i) => {
      const p = s.points.find(p => p[0] === nearest);
      if (p && p[1] !== null) {
        dots[i].setAttribute("cx", sx(p[0])); dots[i].setAttribute("cy", sy(p[1]));
        dots[i].setAttribute("visibility", "visible");
        rows += `<div class="viz-tip-r"><span class="viz-sw" style="background:${s.color}"></span>${s.name}<b>${fmtY(p[1])}</b></div>`;
      } else dots[i].setAttribute("visibility", "hidden");
    });
    tip.innerHTML = rows; tip.hidden = false;
    const left = Math.min(Math.max(sx(nearest) / W * node.clientWidth - 70, 4), node.clientWidth - 150);
    tip.style.left = left + "px";
  });
  svg.addEventListener("pointerleave", () => {
    cross.setAttribute("visibility", "hidden");
    dots.forEach(d => d.setAttribute("visibility", "hidden"));
    tip.hidden = true;
  });
}
