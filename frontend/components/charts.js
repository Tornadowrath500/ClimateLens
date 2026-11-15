/* Chart components: plain SVG, no dependencies. All colour comes from CSS classes/variables in styles.css
 * (fill-old, fill-young, ... and the --score-* / --terrain-* ramps), so charts follow the theme automatically.
 * Every function returns a <figure class="chart"> element ready to append anywhere. */

import { h, svg, clamp, pct, num } from "../utils.js";

const W = 760;
const lin = (d0, d1, r0, r1) => (v) => r0 + ((v - d0) / (d1 - d0 || 1)) * (r1 - r0);
function ticks(lo, hi, n = 5) {
  const span = hi - lo; if (!(span > 0)) return [lo];
  const raw = span / n, mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw);
  const out = []; for (let v = Math.ceil(lo / step - 1e-9) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(10));
  return out;
}
const T = (x, y, text, { cls = "", anchor = "start", rotate } = {}) =>
  svg("text", { x, y, class: `ch-text ${cls}`, "text-anchor": anchor, transform: rotate ? `rotate(${rotate} ${x} ${y})` : null }, text);
const L = (x1, y1, x2, y2, cls = "ch-grid") => svg("line", { x1, y1, x2, y2, class: cls });
const tip = (text) => svg("title", text);

/** Wrap an <svg> in the shared chart container (title, legend, accessible name). */
export function ChartBox({ title, chart, legend, label }) {
  chart.setAttribute("role", "img"); chart.setAttribute("aria-label", label || title || "Chart");
  return h("figure", { class: "chart" }, title && h("p", { class: "chart-title" }, title), chart,
    legend && h("div", { class: "chart-legend" }, legend.map((l) => h("span", h("i", { class: `fill-${l.fill}`, style: l.dashed ? { background: "none", borderTop: "2px dashed currentColor", height: 0, width: "1rem" } : l.style }), l.label))));
}
const frame = (H) => svg("svg", { viewBox: `0 0 ${W} ${H}`, preserveAspectRatio: "xMidYMid meet" });

// ---- horizontal bars (costs, contributions, proxy strength, twin test) ------------------------------------------
export function barH({ rows, xTitle, domain, base = 0, format = (v) => num(v, 2), rowH = 30, title, legend, label }) {
  const labelW = clamp(Math.max(...rows.map((r) => String(r.label).length)) * 6.4 + 18, 90, 330), R = 78, top = 8, bottom = xTitle ? 46 : 26;
  const H = top + rows.length * rowH + bottom, vals = rows.map((r) => r.value).concat(base);
  let [lo, hi] = domain || [Math.min(...vals), Math.max(...vals)];
  if (!domain) { const pad = (hi - lo) * 0.14 || 0.1; if (lo < base) lo -= pad; hi += pad; }
  const x = lin(lo, hi, labelW, W - R), s = frame(H);
  for (const t of ticks(lo, hi, 6)) { s.append(L(x(t), top, x(t), top + rows.length * rowH), T(x(t), top + rows.length * rowH + 16, format(t), { anchor: "middle" })); }
  s.append(L(x(base), top, x(base), top + rows.length * rowH, "ch-axis"));
  rows.forEach((r, i) => {
    const y = top + i * rowH, bh = rowH * 0.62, x0 = x(base), x1 = x(r.value);
    s.append(T(labelW - 10, y + rowH / 2 + 4, r.label, { anchor: "end" }),
      svg("rect", { x: Math.min(x0, x1), y: y + (rowH - bh) / 2, width: Math.max(1, Math.abs(x1 - x0)), height: bh, rx: 3, class: `fill-${r.fill || "old"}` }, tip(r.tip || `${r.label}: ${format(r.value)}`)),
      T(x1 + (r.value >= base ? 6 : -6), y + rowH / 2 + 4, r.text ?? format(r.value), { anchor: r.value >= base ? "start" : "end", cls: "strong" }));
  });
  if (xTitle) s.append(T((labelW + W - R) / 2, H - 6, xTitle, { anchor: "middle" }));
  return ChartBox({ title, chart: s, legend, label });
}

// ---- dot-and-interval panels (group rates with 95% intervals) ------------------------------------------------------
export function dotInterval({ panels, title, legend, label }) {
  const n = panels.length, gap = 40, pw = (W - gap * (n - 1)) / n, rowH = 50, top = 30, bottom = 28;
  const H = top + Math.max(...panels.map((p) => p.rows.length)) * rowH + bottom, s = frame(H);
  panels.forEach((p, pi) => {
    const x0 = pi * (pw + gap), x = lin(0, 1, x0 + 4, x0 + pw - 4), yEnd = top + p.rows.length * rowH;
    s.append(T(x0, 14, p.title, { cls: "title" }));
    for (const t of [0, 0.5, 1]) s.append(L(x(t), top - 6, x(t), yEnd), T(x(t), yEnd + 16, pct(t, 0), { anchor: "middle" }));
    p.rows.forEach((r, i) => {
      const y = top + i * rowH; s.append(T(x0, y + 12, r.label, { cls: "strong" }));
      if (r.value == null) { s.append(T(x0, y + 32, "n/a")); return; }
      const cy = y + 30, cls = r.fill || "old", lo = r.lo ?? r.value, hi = r.hi ?? r.value;
      s.append(L(x(lo), cy, x(hi), cy, `stroke-${cls}`).cloneNode(false), L(x(lo), cy - 5, x(lo), cy + 5, `stroke-${cls}`), L(x(hi), cy - 5, x(hi), cy + 5, `stroke-${cls}`));
      s.lastChild.previousSibling.previousSibling.setAttribute("stroke-width", 2); // interval line
      const mark = r.shape === "diamond"
        ? svg("path", { d: `M${x(r.value)} ${cy - 8}L${x(r.value) + 8} ${cy}L${x(r.value)} ${cy + 8}L${x(r.value) - 8} ${cy}Z`, class: `fill-${cls}` })
        : svg("circle", { cx: x(r.value), cy, r: 6.5, class: `fill-${cls}` });
      mark.append(tip(r.tip || `${r.label}: ${pct(r.value)} (95% interval ${pct(lo)} to ${pct(hi)})`)); s.append(mark);
      const right = x(hi) + 46 < x0 + pw;
      s.append(T(right ? x(hi) + 10 : x(lo) - 10, cy + 4, pct(r.value, 0), { anchor: right ? "start" : "end", cls: "strong" }));
    });
  });
  return ChartBox({ title, chart: s, legend, label: label || "Group rates with 95% intervals" });
}

// ---- threshold sweep: cost on top, group rates below, vertical markers -------------------------------------------------
export function sweepChart({ sweep, marks, young, old, title }) {
  const left = 58, right = 16, pw = W - left - right, t1 = 28, h1 = 150, gap = 44, h2 = 170, bottom = 50, H = t1 + h1 + gap + h2 + bottom;
  const all = sweep.filter((r) => r.group === "All"), g = (name) => sweep.filter((r) => r.group === name);
  const xs = all.map((r) => r.threshold), x = lin(Math.min(...xs), Math.max(...xs), left, left + pw);
  const maxCost = Math.max(...all.map((r) => r.cost_per_applicant)) * 1.1, y1 = lin(0, maxCost, t1 + h1, t1), y2 = lin(0, 1, t1 + h1 + gap + h2, t1 + h1 + gap);
  const s = frame(H), p2top = t1 + h1 + gap;
  s.append(T(left, 16, "Average cost per applicant (all applicants)", { cls: "title" }), T(left, p2top - 10, "Share classified Good, by age group", { cls: "title" }));
  for (const t of ticks(0, maxCost, 4)) s.append(L(left, y1(t), left + pw, y1(t)), T(left - 8, y1(t) + 4, num(t, 1), { anchor: "end" }));
  for (const t of [0, 0.25, 0.5, 0.75, 1]) s.append(L(left, y2(t), left + pw, y2(t)), T(left - 8, y2(t) + 4, pct(t, 0), { anchor: "end" }));
  for (const t of ticks(Math.min(...xs), Math.max(...xs), 9)) s.append(T(x(t), p2top + h2 + 18, num(t, 1), { anchor: "middle" }));
  const path = (rows, yy, key, cls, dash) => svg("path", { d: rows.map((r, i) => `${i ? "L" : "M"}${x(r.threshold).toFixed(1)} ${yy(r[key]).toFixed(1)}`).join(""), class: `ch-line stroke-${cls}`, "stroke-dasharray": dash || null });
  s.append(path(all, y1, "cost_per_applicant", "ink"), path(g(old), y2, "predicted_good_rate", "old"), path(g(young), y2, "predicted_good_rate", "young", "7 5"));
  [...marks].sort((a, b) => a.x - b.x).forEach((m, i) => {
    for (const [a, b] of [[t1, t1 + h1], [p2top, p2top + h2]]) s.append(svg("line", { x1: x(m.x), x2: x(m.x), y1: a, y2: b, class: `stroke-${m.stroke || "muted"}`, "stroke-width": 1.5, "stroke-dasharray": m.solid ? null : "2 4" }));
    s.append(T(x(m.x), t1 - 4 - (i % 2) * 0, m.label, { anchor: "middle", cls: "strong", rotate: null }));
  });
  s.append(T(left + pw / 2, H - 6, "Decision threshold: classify Good when P(Good) is at least this", { anchor: "middle" }));
  return ChartBox({ title, chart: s, label: "Cost and group outcomes across decision thresholds",
    legend: [{ fill: "old", label: old }, { fill: "young", label: young, dashed: true }] });
}

// ---- box plots with every point (repeated-split stability) ---------------------------------------------------------------
const quantile = (a, q) => { const i = (a.length - 1) * q, lo = Math.floor(i); return a[lo] + (a[Math.min(lo + 1, a.length - 1)] - a[lo]) * (i - lo); };
export function boxJitter({ series, xTitle, title }) {
  const left = 190, right = 24, rowH = 86, top = 10, bottom = 50, H = top + series.length * rowH + bottom;
  const all = series.flatMap((r) => r.values), pad = ((Math.max(...all, 0) - Math.min(...all, 0)) * 0.08) || 0.05;
  const lo = Math.min(...all, 0) - pad, hi = Math.max(...all, 0) + pad, x = lin(lo, hi, left, W - right), s = frame(H);
  for (const t of ticks(lo, hi, 7)) s.append(L(x(t), top, x(t), top + series.length * rowH), T(x(t), top + series.length * rowH + 16, pct(t, 0), { anchor: "middle" }));
  s.append(L(x(0), top, x(0), top + series.length * rowH, "ch-zero"));
  series.forEach((r, i) => {
    const v = [...r.values].sort((a, b) => a - b), cy = top + i * rowH + rowH / 2, q1 = quantile(v, 0.25), q2 = quantile(v, 0.5), q3 = quantile(v, 0.75), iqr = q3 - q1;
    const wl = Math.min(...v.filter((d) => d >= q1 - 1.5 * iqr)), wh = Math.max(...v.filter((d) => d <= q3 + 1.5 * iqr));
    s.append(T(left - 12, cy + 4, r.name, { anchor: "end", cls: "strong" }), L(x(wl), cy, x(wh), cy, "stroke-ink"),
      svg("rect", { x: x(q1), y: cy - 18, width: Math.max(1, x(q3) - x(q1)), height: 36, rx: 3, class: "fill-ok", "fill-opacity": 0.35, stroke: "currentColor", "stroke-width": 1.5 }),
      L(x(q2), cy - 18, x(q2), cy + 18, "stroke-ink"));
    r.values.forEach((d, k) => s.append(svg("circle", { cx: x(d), cy: cy + (((k * 37) % 23) - 11) * 1.4, r: 3.6, class: i % 2 ? "fill-young" : "fill-old", "fill-opacity": 0.8 }, tip(`${pct(d)} gap`))));
  });
  s.append(T(left + (W - right - left) / 2, H - 6, xTitle, { anchor: "middle" }));
  return ChartBox({ title, chart: s, label: "Distribution of the age-group gap across repeated splits" });
}

// ---- the applicant map: points over an optional fairness-terrain heat grid -------------------------------------------------------
const ramp = (t, lo, mid, hi) => (t < 0.5 ? `color-mix(in srgb, var(${mid}) ${(t * 200).toFixed(0)}%, var(${lo}))` : `color-mix(in srgb, var(${hi}) ${((t - 0.5) * 200).toFixed(0)}%, var(${mid}))`);
export function scatterMap({ points, terrain, bins, colorBy, kinds, groups, selected, onSelect, explained }) {
  const Hh = 520, m = { l: 34, r: 12, t: 10, b: 34 }, s = frame(Hh);
  const xs = points.map((p) => p.x), ys = points.map((p) => p.y), x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const x = lin(x0, x1, m.l, W - m.r), y = lin(y0, y1, Hh - m.b, m.t);
  if (terrain) for (const c of terrain.filter((c) => c.reliable)) {
    const cx0 = x0 + (c.cx * (x1 - x0)) / bins, cx1 = x0 + ((c.cx + 1) * (x1 - x0)) / bins, cy0 = y0 + (c.cy * (y1 - y0)) / bins, cy1 = y0 + ((c.cy + 1) * (y1 - y0)) / bins;
    s.append(svg("rect", { x: x(cx0), y: y(cy1), width: x(cx1) - x(cx0), height: y(cy0) - y(cy1), class: "ch-cell", style: { fill: ramp(clamp(0.5 + c.gap / 0.8, 0, 1), "--terrain-neg", "--terrain-mid", "--terrain-pos"), fillOpacity: 0.75 } },
      tip(`Region: ${c.n_young} younger / ${c.n_old} older applicants. Classified Good: ${pct(c.rate_young, 0)} vs ${pct(c.rate_old, 0)}. Gap ${(c.gap * 100).toFixed(0)} pts`)));
  }
  const fillFor = (p) => {
    if (colorBy === "Age group") return { cls: p.group === groups.young ? "fill-young" : "fill-old" };
    if (colorBy === "Mistakes") return { cls: p.kind === kinds.false_good ? "fill-costly" : p.kind === kinds.false_bad ? "fill-young" : "fill-ok" };
    if (colorBy === "Actual label") return { cls: p.actual_good ? "fill-old" : "fill-young" };
    return { style: { fill: ramp(p.p_good, "--score-lo", "--score-mid", "--score-hi") } };
  };
  const draw = (p) => {
    const cx = x(p.x), cy = y(p.y), f = fillFor(p), sel = selected === p.i, r = sel ? 8 : 5.5;
    const el = p.group === groups.young
      ? svg("path", { d: `M${cx} ${cy - r}L${cx + r} ${cy}L${cx} ${cy + r}L${cx - r} ${cy}Z` })
      : svg("circle", { cx, cy, r: r * 0.92 });
    el.setAttribute("class", `ch-point ${f.cls || ""}${sel ? " sel" : ""}`); if (f.style) Object.assign(el.style, f.style);
    el.append(tip(`Applicant ${p.i} · ${p.group} · score ${p.p_good.toFixed(2)}`));
    el.addEventListener("click", () => onSelect(p.i)); return el;
  };
  points.filter((p) => p.i !== selected).forEach((p) => s.append(draw(p)));
  const sel = points.find((p) => p.i === selected); if (sel) s.append(draw(sel));
  s.append(T(W / 2, Hh - 8, `Similarity axis 1 (${pct(explained[0], 0)} of variation)`, { anchor: "middle" }), T(10, Hh / 2, `Similarity axis 2 (${pct(explained[1], 0)})`, { anchor: "middle", rotate: -90 }));
  return ChartBox({ chart: s, label: "Map of applicants placed by similarity; click a point to inspect an applicant" });
}

// ---- labelled scatter (mitigation trade-off map) ------------------------------------------------------------------------------------
export function tradeoff({ points, xTitle, yTitle, title }) {
  const m = { l: 62, r: 30, t: 24, b: 50 }, H = 440, xs = points.map((p) => p.x), ys = points.map((p) => p.y);
  const xlo = Math.min(...xs), xhi = Math.max(...xs), xp = (xhi - xlo) * 0.12 || 0.05, yhi = Math.max(...ys) * 1.2 || 0.1;
  const x = lin(xlo - xp, xhi + xp, m.l, W - m.r), y = lin(0, yhi, H - m.b, m.t), s = frame(H);
  for (const t of ticks(0, yhi, 5)) s.append(L(m.l, y(t), W - m.r, y(t)), T(m.l - 8, y(t) + 4, pct(t, 0), { anchor: "end" }));
  for (const t of ticks(xlo - xp, xhi + xp, 6)) s.append(T(x(t), H - m.b + 18, num(t, 2), { anchor: "middle" }));
  const placed = [];
  const free = (b) => !placed.some((q) => b.x < q.x + q.w && b.x + b.w > q.x && b.y < q.y + 14 && b.y + 14 > q.y);
  for (const p of [...points].sort((a, b) => a.x - b.x)) {
    const cx = x(p.x), cy = y(p.y), w = p.label.length * 6.4, mark = p.shape === "diamond"
      ? svg("path", { d: `M${cx} ${cy - 9}L${cx + 9} ${cy}L${cx} ${cy + 9}L${cx - 9} ${cy}Z`, class: `fill-${p.fill || "old"}` })
      : svg("circle", { cx, cy, r: 8, class: `fill-${p.fill || "old"}` });
    mark.append(tip(p.tip)); s.append(mark);
    const spots = [[cx - w / 2, cy - 24], [cx - w / 2, cy + 12], [cx + 12, cy - 6], [cx - w - 12, cy - 6]];
    const [bx, by] = spots.find(([bx, by]) => free({ x: bx, y: by, w })) || spots[0];
    placed.push({ x: bx, y: by, w }); s.append(T(bx + w / 2, by + 11, p.label, { anchor: "middle", cls: "strong" }));
  }
  s.append(T(m.l + (W - m.l - m.r) / 2, H - 6, xTitle, { anchor: "middle" }), T(14, H / 2, yTitle, { anchor: "middle", rotate: -90 }));
  return ChartBox({ title, chart: s, label: "Trade-off between cost and group gap for each strategy" });
}
