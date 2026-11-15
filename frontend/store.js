/* Client-side state: the replacement for Streamlit's st.session_state.
 * Persistent preferences live in localStorage; the per-tab session id lives in sessionStorage
 * (like a Streamlit session, it ends with the tab and scopes the pinned test review and uploads). */

const KEY = "fairlens.settings";
const DEFAULTS = {
  source: "real",                      // "real" | "demo" (synthetic)
  model: "Logistic regression",
  useAge: true, useStatus: true,       // inputs the model may use
  theme: "auto",                       // "auto" | "light" | "dark"
  rule: { mode: "single", threshold: 0.5, tYoung: 0.5, tOld: 0.5 },   // the shared decision rule
};

function load() {
  try { return { ...DEFAULTS, ...JSON.parse(localStorage.getItem(KEY) || "{}") }; } catch { return { ...DEFAULTS }; }
}
let state = load();
const listeners = new Set();

export const store = {
  get: () => state,
  set(patch) {
    const prev = state;
    state = { ...state, ...patch };
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch { /* private mode: keep in memory */ }
    listeners.forEach((fn) => fn(state, prev));
  },
  subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
  handoff: null,                       // one-shot data passed between pages (e.g. map -> simulator)
};

export function sessionId() {
  try {
    let id = sessionStorage.getItem("fairlens.session");
    if (!id) { id = (crypto.randomUUID ? crypto.randomUUID() : String(Math.random()).slice(2) + Date.now()).replace(/[^A-Za-z0-9_-]/g, ""); sessionStorage.setItem("fairlens.session", id); }
    return id;
  } catch { return (sessionId.fallback ||= "tab" + Math.random().toString(36).slice(2, 14)); }
}

// ---- derived request payloads: what the API calls "settings" and "decision_rule" ----------------------
const AGE = "Attribute13", STATUS = "Attribute9";
export const excluded = (s = state) => [!s.useAge && AGE, !s.useStatus && STATUS].filter(Boolean);
export const settingsPayload = (s = state) => ({ source: s.source, model: s.model, excluded: excluded(s) });
export function rulePayload(meta, s = state) {
  const r = s.rule;
  return r.mode === "group"
    ? { threshold: 0.5, per_group: { [meta.groups.young]: r.tYoung, [meta.groups.old]: r.tOld } }
    : { threshold: r.threshold };
}
export const requestBody = (meta, extra = {}, s = state) => ({ ...settingsPayload(s), decision_rule: rulePayload(meta, s), ...extra });
/** A string that changes whenever the model configuration changes (to detect stale cached results). */
export const configKey = (s = state) => JSON.stringify([s.source, s.model, excluded(s)]);
