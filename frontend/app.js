import { api, ApiError } from "./api.js";
import { store, settingsPayload, requestBody } from "./store.js";
import { h } from "./utils.js";

const pages = [
  ["overview", "Overview", "01"], ["data", "Understand the data", "02"],
  ["evaluation", "Model evaluation", "03"], ["groups", "Group outcomes", "04"],
  ["experiment", "Experiment lab", "05"], ["report", "Findings & report", "06"],
  ["methodology", "Methodology", "07"], ["map", "Applicant map", "08"],
  ["simulator", "Applicant simulator", "09"], ["proxies", "Proxy detector", "10"],
  ["mitigation", "Mitigation lab", "11"], ["byom", "Audit your model", "12"],
];
const $ = (s, root = document) => root.querySelector(s);
const esc = (v) => String(v ?? "—");
let meta = null;
let current = location.hash.slice(1) || "overview";
let busy = false;

function button(label, fn, kind = "secondary") { return h("button", { class: `button ${kind}`, onclick: fn }, label); }
function card(title, body, eyebrow = "") { return h("section", { class: "card" }, eyebrow && h("div", { class: "eyebrow" }, eyebrow), h("h2", title), body); }
function metric(label, value, note = "") { return h("div", { class: "metric" }, h("span", { class: "metric-label" }, label), h("strong", value), note && h("small", note)); }
function table(rows, cols) {
  if (!rows?.length) return h("p", { class: "muted" }, "No rows available.");
  return h("div", { class: "table-wrap" }, h("table", {}, h("thead", {}, h("tr", {}, cols.map(([k, l]) => h("th", { scope: "col" }, l)))), h("tbody", {}, rows.map((r) => h("tr", {}, cols.map(([k]) => h("td", esc(typeof r[k] === "number" ? Number(r[k]).toFixed(3) : r[k]))))))));
}
function nav() {
  const side = $("#sidebar"); side.replaceChildren(
    h("a", { class: "brand", href: "#overview" }, h("span", { class: "brand-mark" }, "F"), h("span", {}, h("strong", "FairLens"), h("small", "MODEL AUDIT WORKSPACE"))),
    h("div", { class: "nav-label" }, "WORKSPACE"),
    ...pages.map(([id, label, n]) => h("a", { class: `nav-link ${current === id ? "active" : ""}`, href: `#${id}` }, h("span", { class: "nav-number" }, n), label)),
    h("div", { class: "sidebar-bottom" }, h("span", { class: "status-dot" }), "Educational benchmark", h("small", "Not a lending system"))
  );
}
function shell(title, intro, content) {
  const s = store.get();
  const main = $("#main"); main.replaceChildren(
    h("header", { class: "topbar" }, h("button", { class: "menu-btn", "aria-label": "Open navigation", onclick: () => document.body.classList.toggle("nav-open") }, "☰"), h("span", { class: "topbar-label" }, "FAIRNESS REVIEW / " + title.toUpperCase()), h("button", { class: "theme-toggle", onclick: () => store.set({ theme: s.theme === "dark" ? "light" : "dark" }) }, s.theme === "dark" ? "Light theme" : "Dark theme")),
    h("div", { class: "page-content" }, h("div", { class: "page-heading" }, h("div", {}, h("div", { class: "eyebrow" }, "FAIRLENS / REVIEW"), h("h1", title), h("p", intro)), settings()),
      h("div", { class: "notice" }, h("strong", "Educational prototype"), " · Historical benchmark data. Group differences are investigation signals, not proof of discrimination."),
      content)
  );
}
function settings() {
  const s = store.get();
  return h("div", { class: "settings" },
    h("label", {}, "DATA SOURCE", h("select", { onchange: (e) => store.set({ source: e.target.value }) }, ["real", "demo"].map((v) => h("option", { value: v, selected: s.source === v }, v === "real" ? "UCI benchmark" : "Synthetic demo")))),
    h("label", {}, "MODEL", h("select", { onchange: (e) => store.set({ model: e.target.value }) }, ["Logistic regression", "Random forest"].map((v) => h("option", { value: v, selected: s.model === v }, v)))),
    h("label", { class: "check-setting" }, h("input", { type: "checkbox", checked: s.useAge, onchange: (e) => store.set({ useAge: e.target.checked }) }), "Use age"),
    h("label", { class: "check-setting" }, h("input", { type: "checkbox", checked: s.useStatus, onchange: (e) => store.set({ useStatus: e.target.checked }) }), "Use status/sex")
  );
}
async function load(title, intro, fn) {
  busy = true; render();
  try { const data = await fn(); renderPage(title, intro, data); }
  catch (e) { renderError(title, intro, e); }
  finally { busy = false; }
}
function renderError(title, intro, error) {
  const message = error instanceof ApiError && error.code === "dataset_missing"
    ? "The UCI data are not installed on this server. Download the benchmark from the Data page or switch to Synthetic demo."
    : error.message || "The request could not be completed.";
  shell(title, intro, h("section", { class: "card error-card" }, h("div", { class: "eyebrow" }, "NEEDS ATTENTION"), h("h2", "This view could not load"), h("p", message), button("Retry", () => route())));
}
function renderSimulator(title, intro, schema) {
  const form = h("form", { class: "profile-form" });
  for (const f of schema.features || []) {
    const initial = schema.typical?.[f.column];
    const control = f.type === "numeric"
      ? h("input", { name:f.column, type:"number", min:f.min, max:f.max, step:"1", value:initial })
      : h("select", { name:f.column }, (f.levels || []).map((level) => h("option", { value:level.value, selected:String(initial)===String(level.value) }, level.label)));
    form.append(h("label", { class:"profile-field" }, h("span", f.label), control, h("small", f.description || "")));
  }
  const outcome = h("div", { class:"sim-result" });
  const evaluate = async (profile) => {
    outcome.replaceChildren(h("p", {class:"muted"}, "Scoring applicant…"));
    try { const result = await api.simEvaluate(body({profile})); outcome.replaceChildren(h("pre", {class:"json-view"}, JSON.stringify(result,null,2))); }
    catch (e) { outcome.replaceChildren(h("p", {class:"error-text"}, e.message)); }
  };
  form.addEventListener("submit", (e) => {
    e.preventDefault(); const profile={};
    for (const f of schema.features || []) { const raw=new FormData(form).get(f.column); profile[f.column]=f.type==="numeric"?Number(raw):raw; }
    evaluate(profile);
  });
  const randomButton = button("Random training applicant", async () => {
    try {
      const r = await api.simRandom(store.get().source);
      for (const field of form.elements) if (r.profile?.[field.name] != null) field.value = r.profile[field.name];
    } catch (e) { outcome.replaceChildren(h("p", { class:"error-text" }, e.message)); }
  });
  const profileBody = h("div", {},
    h("p", { class:"muted" }, `Starting from ${schema.start_label || "a typical applicant"}. Edit fields to explore model behavior.`),
    h("div", { class:"row section" }, randomButton), form,
    button("Evaluate profile", () => form.requestSubmit(), "primary")
  );
  shell(title, intro, h("div", { class:"content-grid" },
    card("Applicant profile", profileBody),
    card("Model response", outcome, "WHAT-IF REVIEW")
  ));
}
function renderPage(title, intro, data) {
  const action = current === "experiment" ? h("div", { class: "row section" },
      button("Pin final test review", async () => { try { const result = await api.pin(body()); renderPage("Final review pinned", "The test set is now frozen for this browser session.", result); } catch (e) { renderError(title, intro, e); } }, "primary"))
    : current === "report" ? h("div", { class: "row section" },
      button("Download Markdown report", async () => { try { const md = await api.reportMarkdown(); const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([md], {type:"text/markdown"})); a.download="fairlens_report.md"; a.click(); URL.revokeObjectURL(a.href); } catch (e) { renderError(title, intro, e); } }, "primary"))
    : current === "data" && store.get().source === "real" ? h("div", { class: "row section" },
      button("Download UCI benchmark", async () => { try { await api.downloadData(); await route(); } catch (e) { renderError(title, intro, e); } }, "primary"))
    : null;
  const content = h("div", { class: "content-grid" },
    card("At a glance", h("div", { class: "metrics-grid" }, Object.entries(data).filter(([,v]) => typeof v === "number" || typeof v === "string").slice(0, 4).map(([k,v]) => metric(k.replaceAll("_", " "), typeof v === "number" ? Number(v).toLocaleString(undefined,{maximumFractionDigits:3}) : v)))),
    card("Response details", h("pre", { class: "json-view" }, JSON.stringify(data, null, 2)), "API CONNECTED")
  );
  shell(title, intro, h("div", {}, action, content));
}
const body = (extra = {}) => requestBody(meta || { groups: { young: "under 25", old: "25 or older" } }, extra);

async function route() {
  current = pages.some(([id]) => id === location.hash.slice(1)) ? location.hash.slice(1) : "overview";
  nav();
  if (busy) return;
  const src = store.get().source;
  const page = pages.find(([id]) => id === current);
  const title = page[1];
  const intro = ({ overview:"A clear view of model behavior, evidence, and trade-offs.", data:"Inspect the source, scope, composition, and limits of the benchmark.", evaluation:"Compare candidate models and reference baselines on validation data.", groups:"Compare outcome and error rates with their denominators and uncertainty.", experiment:"Explore decision thresholds using validation data, then pin one final review.", report:"Review evidence from the pinned test evaluation and export a report.", methodology:"Understand metric definitions, assumptions, and limitations.", map:"Explore applicant outcomes and the model’s decision landscape.", simulator:"Change applicant attributes and inspect scores, explanations, and what-ifs.", proxies:"Measure whether other inputs carry information about sensitive attributes.", mitigation:"Compare mitigation strategies and the trade-offs they produce.", byom:"Upload a decision table and inspect group differences in your own model." })[current];
  if (current === "overview") return load(title, intro, async () => { meta = await api.meta(); const [health,status] = await Promise.all([api.health(), api.dataStatus()]); return { status:health.status, version:health.core_version, data_source:src, benchmark_available:status.real_available, pages_available:pages.length }; });
  if (current === "data") return load(title,intro,async()=>{ if(src === "demo") return api.dataOverview(src); const status=await api.dataStatus(); if(!status.real_available) return { benchmark_available:false, action:"Download the UCI benchmark to continue.", demo_available:true }; return api.dataOverview(src); });
  if (current === "evaluation") return load(title,intro,()=>api.evaluation(settingsPayload()));
  if (current === "groups") return load(title,intro,()=>api.groupsReview(body()));
  if (current === "experiment") return load(title,intro,()=>api.sweep(body()));
  if (current === "report") return load(title,intro,()=>api.findings());
  if (current === "methodology") return load(title,intro,()=>api.methodology(src));
  if (current === "map") return load(title,intro,()=>api.map(body()));
  if (current === "simulator") { try { const schema=await api.simSchema(src); renderSimulator(title,intro,schema); } catch(e) { renderError(title,intro,e); } return; }
  if (current === "proxies") return load(title,intro,()=>api.proxyReport({source:src}));
  if (current === "mitigation") return load(title,intro,()=>api.mitigation({source:src,model:store.get().model}));
  if (current === "byom") return shell(title,intro,h("section",{class:"card"},h("h2","Upload a decision table"),h("p","CSV remains in memory for this browser session. Include a model decision column and a group column."),h("input",{type:"file",accept:".csv,text/csv",id:"byom-file"}),button("Upload CSV",async()=>{try{const file=$("#byom-file").files[0];if(!file)throw new Error("Choose a CSV file first.");const result=await api.byomUpload(file);renderPage(title,intro,result);}catch(e){renderError(title,intro,e);}},"primary")));
}
function render() {
  document.documentElement.dataset.theme = store.get().theme;
  nav();
  if (busy) shell("Loading", "Getting the latest result from the FairLens API.", h("div", { class: "card loading" }, "Loading…"));
}
window.addEventListener("hashchange", route);
window.addEventListener("click", (e) => { if (e.target.closest?.(".nav-link")) document.body.classList.remove("nav-open"); });
store.subscribe(() => { if (!busy) route(); else render(); });
route();
