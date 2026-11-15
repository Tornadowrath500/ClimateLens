/* Small, dependency-free helpers. Text is always inserted as text (never innerHTML), so API strings cannot inject markup. */

const SVG_NS = "http://www.w3.org/2000/svg";
const PROPS = new Set(["value", "checked", "selected", "disabled", "indeterminate"]);

function apply(el, attrs) {
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === "class") el.setAttribute("class", v);
    else if (k === "style" && typeof v === "object") Object.assign(el.style, v);
    else if (k.startsWith("on") && typeof v === "function") el.addEventListener(k.slice(2).toLowerCase(), v);
    else if (PROPS.has(k)) el[k] = v;
    else el.setAttribute(k, v === true ? "" : v);
  }
}
function append(el, kids) {
  for (const kid of kids.flat(Infinity)) {
    if (kid == null || kid === false) continue;
    el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return el;
}
const isAttrs = (a) => a && typeof a === "object" && !a.nodeType && !Array.isArray(a);

/** h("div", {class: "card"}, child, "text") -> HTMLElement */
export function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  if (isAttrs(attrs)) apply(el, attrs); else kids.unshift(attrs);
  return append(el, kids);
}
/** svg("circle", {cx: 1}) -> SVGElement */
export function svg(tag, attrs, ...kids) {
  const el = document.createElementNS(SVG_NS, tag);
  if (isAttrs(attrs)) apply(el, attrs); else kids.unshift(attrs);
  return append(el, kids);
}
export const frag = (...kids) => append(document.createDocumentFragment(), kids);

/** Render "**bold**" spans from backend sentences safely. */
export function rich(text) {
  return frag(String(text ?? "").split(/(\*\*[^*]+\*\*)/g).filter(Boolean).map((part) =>
    part.startsWith("**") ? h("strong", part.slice(2, -2)) : part));
}

// ---- number formatting (null/NaN => "n/a") ------------------------------------------------------
const isNum = (x) => typeof x === "number" && Number.isFinite(x);
export const pct = (x, d = 1) => (isNum(x) ? `${(100 * x).toFixed(d)}%` : "n/a");
export const spct = (x, d = 1) => (isNum(x) ? `${x >= 0 ? "+" : "-"}${Math.abs(100 * x).toFixed(d)}%` : "n/a");
export const pts = (x, d = 1) => (isNum(x) ? `${x >= 0 ? "+" : "-"}${Math.abs(100 * x).toFixed(d)} pts` : "n/a");
export const num = (x, d = 2) => (isNum(x) ? x.toFixed(d) : "n/a");
export const snum = (x, d = 2) => (isNum(x) ? `${x >= 0 ? "+" : "-"}${Math.abs(x).toFixed(d)}` : "n/a");
export const int = (x) => (isNum(x) ? Math.round(x).toLocaleString("en-US") : "n/a");
export const plural = (n, one, many = one + "s") => `${int(n)} ${n === 1 ? one : many}`;

export const clamp = (x, lo, hi) => Math.min(hi, Math.max(lo, x));
export function debounce(fn, ms = 200) { let t; const d = (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; d.cancel = () => clearTimeout(t); return d; }
export const isAbort = (e) => e && (e.name === "AbortError" || e.code === "aborted");
export const uid = (p = "id") => `${p}-${Math.random().toString(36).slice(2, 9)}`;

// ---- downloads -----------------------------------------------------------------------------------
export function downloadBlob(content, filename, type) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const a = h("a", { href: url, download: filename });
  document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
/** CSV with spreadsheet-formula protection: text cells starting with = + - @ are prefixed with a quote. */
export function toCsv(rows, columns) {
  const cols = columns || (rows[0] ? Object.keys(rows[0]) : []);
  const cell = (v) => {
    if (v == null) return "";
    let s = String(v);
    if (typeof v === "string" && /^[=+\-@\t\r]/.test(s) && Number.isNaN(Number(s))) s = `'${s}`;
    return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  return [cols.join(","), ...rows.map((r) => cols.map((c) => cell(r[c])).join(","))].join("\n") + "\n";
}
export const downloadCsv = (rows, filename, columns) => downloadBlob(toCsv(rows, columns), filename, "text/csv");