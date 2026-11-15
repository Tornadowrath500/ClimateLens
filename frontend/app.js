import { api, ApiError } from "./api.js";
import { store, settingsPayload, requestBody } from "./store.js";
import { h } from "./utils.js";
import { scatterMap, barH } from "./components/charts.js";

const pages = [
  ["overview", "Overview", "01", "Start here"], ["data", "Understand the data", "02", "Start here"],
  ["evaluation", "Model evaluation", "03", "Review evidence"], ["groups", "Group outcomes", "04", "Review evidence"],
  ["map", "Applicant map", "05", "Explore cases"], ["simulator", "Applicant simulator", "06", "Explore cases"],
  ["experiment", "Experiment lab", "07", "Explore trade-offs"], ["mitigation", "Mitigation lab", "08", "Explore trade-offs"],
  ["proxies", "Proxy detector", "09", "Explore trade-offs"], ["byom", "Audit your model", "10", "Explore trade-offs"],
  ["report", "Findings & report", "11", "Wrap up"], ["methodology", "Methodology & limits", "12", "Wrap up"],
];
const $ = (s, root = document) => root.querySelector(s);
const esc = (v) => String(v ?? "—");
let meta = null;
let current = location.hash.slice(1) || "overview";
let busy = false;
let byomUpload = null;
let byomResult = null;
const mapOptions = { colorBy:"Model score", terrain:true, includeTrain:false, bins:5, minPerGroup:5, selected:0 };

function button(label, fn, kind = "secondary") { return h("button", { class: `button ${kind}`, onclick: fn }, label); }
function card(title, body, eyebrow = "") { return h("section", { class: "card" }, eyebrow && h("div", { class: "eyebrow" }, eyebrow), h("h2", title), body); }
function metric(label, value, note = "") { return h("div", { class: "metric" }, h("span", { class: "metric-label" }, label), h("strong", value), note && h("small", note)); }
const nice = (key) => String(key).replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
const displayValue = (value) => {
  if (value == null) return "Not available";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") return Number.isInteger(value) ? value.toLocaleString() : Number(value).toLocaleString(undefined,{maximumFractionDigits:4});
  if (typeof value === "string") return value;
  return JSON.stringify(value);
};
function table(rows, cols) {
  if (!rows?.length) return h("p", { class: "muted" }, "No rows available.");
  return h("div", { class: "table-wrap" }, h("table", {class:"data"}, h("thead", {}, h("tr", {}, cols.map(([k, l]) => h("th", { scope: "col" }, l)))), h("tbody", {}, rows.map((r) => h("tr", {}, cols.map(([k]) => h("td", displayValue(r[k]))))))));
}
function nav() {
  const side = $("#sidebar"); side.replaceChildren(
    h("a", { class: "brand", href: "#overview" }, h("span", { class: "brand-mark" }, "F"), h("span", {}, h("strong", "FairLens"), h("small", "MODEL AUDIT WORKSPACE"))),
    h("p",{class:"sidebar-hint"},"A guided review of model data, performance, and fairness signals."),
    ...[...new Set(pages.map((p)=>p[3]))].map((section)=>h("section",{class:"nav-section"},h("div",{class:"nav-title"},section),...pages.filter((p)=>p[3]===section).map(([id,label,n])=>h("a",{class:`nav-link ${current===id?"active":""}`,href:`#${id}`,...(current===id?{"aria-current":"page"}:{})},h("span",{class:"nav-icon", "aria-hidden":"true"},({overview:"◈",data:"▤",evaluation:"⌁",groups:"◎",map:"⌖",simulator:"⊙",experiment:"⌘",mitigation:"◉",proxies:"⌗",byom:"↗",report:"▧",methodology:"∴"})[id]),h("span",{class:"nav-number"},n),h("span",{class:"nav-text"},label))))),
    h("div", { class: "sidebar-bottom" }, h("span", { class: "status-dot" }), "Educational prototype", h("small", "Never use for real lending decisions"))
  );
}
function shell(title, intro, content) {
  const s = store.get();
  const notice = s.source === "demo"
    ? "Synthetic demo records are invented and must not be presented as real evidence. FairLens is not a lending system."
    : "The benchmark is historical and does not represent current applicants. Group differences are investigation signals, not proof of discrimination.";
  const main = $("#main"); main.replaceChildren(
    h("header", { class: "topbar" }, h("button", { class: "menu-btn", "aria-label": "Open navigation", onclick: () => document.body.classList.toggle("nav-open") }, "☰"), h("span", { class: "topbar-label" }, "FAIRNESS REVIEW / " + title.toUpperCase()), h("button", { class: "theme-toggle", "aria-label": s.theme === "dark" ? "Switch to light theme" : "Switch to dark theme", title: s.theme === "dark" ? "Switch to light theme" : "Switch to dark theme", onclick: () => store.set({ theme: s.theme === "dark" ? "light" : "dark" }) }, h("span",{class:"theme-icon","aria-hidden":"true"},s.theme === "dark" ? "☀" : "☾"),h("span",{class:"theme-label"},s.theme === "dark" ? "Light" : "Dark"))),
    h("div", { class: "page-content" }, h("div", { class: "page-heading" }, h("div", {}, h("div", { class: "eyebrow" }, `${pages.find((p)=>p[0]===current)?.[3] || "FAIRLENS"} / STEP ${pages.findIndex((p)=>p[0]===current)+1} OF ${pages.length}`), h("h1", title), h("p", intro)), settings()),
      h("div", { class: `notice ${s.source === "demo" ? "demo" : ""}` }, h("strong", s.source === "demo" ? "Synthetic data" : "Historical benchmark"), " · ", notice),
      content)
  );
}
function settings() {
  const s = store.get();
  return h("div", { class: "settings" },
    h("label", {}, "DATA", h("select", { "aria-label":"Data source", onchange: (e) => store.set({ source: e.target.value }) }, ["real", "demo"].map((v) => h("option", { value: v, selected: s.source === v }, v === "real" ? "UCI benchmark" : "Synthetic demo")))),
    h("label", {}, "MODEL", h("select", { onchange: (e) => store.set({ model: e.target.value }) }, ["Logistic regression", "Random forest"].map((v) => h("option", { value: v, selected: s.model === v }, v)))),
    h("label", { class: "check-setting", title:"Include age as an input to the model" }, h("input", { type: "checkbox", checked: s.useAge, onchange: (e) => store.set({ useAge: e.target.checked }) }), "Include age input"),
    h("label", { class: "check-setting", title:"Include the combined personal status and sex field as an input" }, h("input", { type: "checkbox", checked: s.useStatus, onchange: (e) => store.set({ useStatus: e.target.checked }) }), "Include status/sex input"),
    h("span",{class:"settings-help"},"These are sensitive model inputs. Removing them does not remove correlated proxies.")
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
  const next=error?.code==="no_pinned_review"?button("Go to Experiment lab",()=>{location.hash="#experiment"},"primary")
    :error?.code==="dataset_missing"?button("Use synthetic demo data",()=>store.set({source:"demo"}),"primary"):null;
  shell(title, intro, h("section", { class: "card error-card" }, h("div", { class: "eyebrow" }, "NEEDS ATTENTION"), h("h2", "This view could not load"), h("p", message),h("div",{class:"row"},next,button("Retry", () => route()))));
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
    try { const result = await api.simEvaluate(body({profile})); outcome.replaceChildren(simulatorResult(result)); }
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
function simulatorResult(result) {
  const reasons=(result.explain||[]).slice(0,8).map((r)=>({label:r.feature,value:r.contribution,fill:r.contribution>=0?"old":"young"}));
  return h("div",{class:"sim-result-content"},
    h("div",{class:"prediction-card"},h("span",{class:"eyebrow"},"MODEL OUTPUT"),h("strong",{class:result.decision==="Good"?"decision-good":"decision-bad"},result.decision||"Result unavailable"),h("p",`${(result.score*100).toFixed(1)}% estimated probability of Good · ${(result.threshold*100).toFixed(0)}% decision threshold`),h("small","This is a model estimate for an illustrative profile, not a credit recommendation.")),
    h("div",{class:"sim-result-section"},h("h3","What influenced the score?"),barH({rows:reasons,xTitle:"Contribution to Good-risk score",format:(v)=>`${v>0?"+":""}${(v*100).toFixed(0)} pts`,label:"Largest input contributions to the applicant score"})),
    h("div",{class:"sim-result-section"},h("h3","Sensitive attribute twin test"),h("p",`${result.twin_flips||0} alternate profile${result.twin_flips===1?"":"s"} changed the model decision when sensitive attributes changed.`),h("small","This diagnostic tests model sensitivity in the benchmark; it does not establish a real-world outcome.")),
    h("details",{class:"result-details"},h("summary","All explanations, one-input changes, and what-if path"),valueView("complete result",result))
  );
}
async function renderApplicantMap(title, intro) {
  const config = store.get();
  const request = (extra = {}) => requestBody(meta || {groups:{young:"under 25",old:"25 or older"}}, {
    include_train:mapOptions.includeTrain, bins:mapOptions.bins, min_per_group:mapOptions.minPerGroup, ...extra
  });
  const choose = (i) => { mapOptions.selected=i; renderApplicantMap(title,intro); };
  let data, applicant;
  try {
    data = await api.map(request());
    applicant = await api.mapApplicant(request({index:mapOptions.selected}));
  } catch (e) { renderError(title,intro,e); return; }

  const select = (label, options, value, change) => h("label", {class:"map-control"},label,
    h("select", {value, onchange:(e)=>{change(e.target.value);renderApplicantMap(title,intro);}},options.map((v)=>h("option",{value:v,selected:value===v},v))));
  const controls = h("div", {class:"map-controls"},
    select("COLOUR BY",["Model score","Age group","Mistakes","Actual label"],mapOptions.colorBy,(v)=>mapOptions.colorBy=v),
    select("TERRAIN GRID",[3,4,5,6,7,8].map(String),String(mapOptions.bins),(v)=>mapOptions.bins=Number(v)),
    select("MINIMUM PER GROUP",[3,5,8,10,12,15].map(String),String(mapOptions.minPerGroup),(v)=>mapOptions.minPerGroup=Number(v)),
    h("label",{class:"map-check"},h("input",{type:"checkbox",checked:mapOptions.terrain,onchange:(e)=>{mapOptions.terrain=e.target.checked;renderApplicantMap(title,intro);}}),"Fairness terrain"),
    h("label",{class:"map-check"},h("input",{type:"checkbox",checked:mapOptions.includeTrain,onchange:(e)=>{mapOptions.includeTrain=e.target.checked;mapOptions.selected=0;renderApplicantMap(title,intro);}}),"Include training applicants")
  );
  const chart = scatterMap({points:data.points,terrain:mapOptions.terrain?data.terrain:[],bins:data.bins,colorBy:mapOptions.colorBy,kinds:data.kinds,groups:data.groups,selected:mapOptions.selected,onSelect:choose,explained:data.explained});
  const summary=data.terrain_summary||{};
  const summaryBlock=summary.regions
    ? h("div",{class:"terrain-summary"},h("strong",`${summary.regions} reliable regions`),h("p",`Across ${summary.applicants_covered} applicants, younger and older look-alikes have a weighted classified-Good gap of ${(Math.abs(summary.weighted_gap)*100).toFixed(1)} points.`),h("small","A difference is a signal to investigate, not proof of discrimination or its cause."))
    : h("div",{class:"terrain-summary muted"},"No region has enough applicants from both groups. Try a coarser grid, a lower minimum, or include training applicants.");
  const pointCount=h("span",{class:"map-caption"},`${data.n} applicants · ${mapOptions.includeTrain?"training + validation":"validation only"} · Similarity uses non-sensitive inputs`);
  const selectedTable=table(applicant.profile||[],[["label","Input"],["value","Value"]]);
  const explanation=(applicant.explain||[]).slice(0,8).map((r)=>({label:r.feature,value:r.contribution,fill:r.contribution>=0?"old":"young",tip:`${r.feature}: ${r.contribution>=0?"raises":"lowers"} the Good-risk score`}));
  const people=applicant.look_alikes||{};
  const applicantPanel=h("div",{class:"applicant-detail"},
    h("div",{class:"applicant-heading"},h("div",{},h("div",{class:"eyebrow"},`APPLICANT ${applicant.index} · ${applicant.part||"validation"}`),h("h2",applicant.group||"Applicant")),
      h("div",{class:"score-pill"},h("strong",`${(applicant.score*100).toFixed(0)}%`),h("small","estimated Good"))),
    h("p",{class:"muted"},`Labeled ${applicant.actual_good?"Good":"Bad"} in the historical data. Decision threshold: ${(applicant.threshold*100).toFixed(0)}%.`),
    h("div",{class:"map-detail-grid"},card("Applicant profile",selectedTable),card("Why this score?",barH({rows:explanation,xTitle:"Change in model score",format:(v)=>`${v>0?"+":""}${(v*100).toFixed(0)} pts`,title:"Input contributions",label:"Inputs that raise or lower this model score"}))),
    h("div",{class:"lookalike-row"},["same","other"].map((key)=>{const q=people[key]||{};return h("div",{class:"lookalike-card"},h("span",key==="same"?"Same age group":"Other age group"),h("strong",q.n?`${(q.classified_good*100).toFixed(0)}% classified Good`:"No matches"),h("small",`${q.n||0} closest · ${(100*(q.actual_good||0)).toFixed(0)}% labelled Good`));})),
    applicant.path?.steps?.length?h("details",{class:"path-detail"},h("summary","What changes could flip this decision?"),table(applicant.path.steps,[["feature","Input"],["from","Current"],["to","Alternative"],["p_after","Score after"]]),h("small",applicant.path.flipped?"The example path flips the model decision. This describes model behavior, not advice to an applicant.":"The tested changes did not flip the model decision.")):null
  );
  shell(title,intro,h("div",{class:"map-page"},controls,
    h("section",{class:"card map-card"},chart,pointCount,summaryBlock),
    applicantPanel
  ));
}
function renderByom(title,intro) {
  const uploadPanel=h("section",{class:"card upload-panel"},h("h2",byomUpload?"Decision table ready":"Add a decision table"),
    h("p",byomUpload?`${byomUpload.name} · ${byomUpload.rows.toLocaleString()} rows · ${byomUpload.n_columns} columns`:"Upload a CSV or use FairLens validation predictions as a sample. Files are kept in memory for this browser session and are not saved to disk."),
    !byomUpload&&h("div",{class:"row"},h("input",{type:"file",accept:".csv,text/csv",id:"byom-file"}),button("Upload CSV",async()=>{try{const file=$("#byom-file").files[0];if(!file)throw new Error("Choose a CSV file first.");byomUpload=await api.byomUpload(file);byomResult=null;renderByom(title,intro);}catch(e){renderError(title,intro,e);}},"primary"),button("Use FairLens sample",async()=>{try{byomUpload=await api.byomSample(settingsPayload());byomResult=null;renderByom(title,intro);}catch(e){renderError(title,intro,e);}})));
  if(!byomUpload){shell(title,intro,h("div",{class:"byom-page"},uploadPanel,h("aside",{class:"reading-guide"},h("strong","What you need"),h("p","The CSV needs a decision or score column and a group column with 2 to 20 groups. Add an actual-outcome column if you also want error rates."))));return;}
  const columns=byomUpload.columns||[], suggested=byomUpload.suggested||{};
  const colOptions=columns.map(c=>c.name);
  const decisionDefault=suggested.decision_column||colOptions[0]||"";
  const groupDefault=suggested.group_column||colOptions.find(n=>n!==decisionDefault)||"";
  const selectField=(label,id,options,value)=>h("label",{class:"byom-field"},label,h("select",{id},options.map((v)=>h("option",{value:v,selected:v===value},v))));
  const form=h("div",{class:"byom-form"},
    selectField("MODEL DECISION OR SCORE","byom-decision",colOptions,decisionDefault),
    selectField("GROUP TO COMPARE","byom-group",colOptions.filter(c=>c!==decisionDefault),groupDefault),
    selectField("KNOWN ACTUAL OUTCOME (OPTIONAL)","byom-truth",["(No actual outcomes)",...colOptions.filter(c=>c!==decisionDefault&&c!==groupDefault)],suggested.truth_column||"(No actual outcomes)"),
    h("label",{class:"byom-field"},"FAVORABLE DECISION VALUE (IF LABELS)",h("select",{id:"byom-favorable"},(columns.find(c=>c.name===decisionDefault)?.values||[]).map((v)=>h("option",{value:v,selected:v===suggested.favorable_value},v)))),
    h("label",{class:"byom-field"},"POSITIVE ACTUAL VALUE (IF PROVIDED)",h("select",{id:"byom-truth-positive"},(columns.find(c=>c.name===suggested.truth_column)?.values||[]).map((v)=>h("option",{value:v,selected:v===suggested.truth_positive_value},v)))),
    h("label",{class:"byom-field"},"SCORE CUTOFF (IF NUMERIC SCORE)",h("input",{id:"byom-threshold",type:"number",step:"any",value:columns.find(c=>c.name===decisionDefault)?.median??""})),
    selectField("REFERENCE GROUP (OPTIONAL)","byom-reference",["(Automatic)",...(columns.find(c=>c.name===groupDefault)?.values||[])],"(Automatic)")
  );
  const replaceChoices=(el,values,preferred)=>{el.replaceChildren(...values.map(v=>h("option",{value:v},v)));if(values.includes(preferred))el.value=preferred;};
  $("#byom-decision",form).addEventListener("change",(e)=>{const c=columns.find(x=>x.name===e.target.value);replaceChoices($("#byom-favorable",form),c?.values||[],suggested.favorable_value);$("#byom-threshold",form).value=c?.median??"";});
  $("#byom-group",form).addEventListener("change",(e)=>{const c=columns.find(x=>x.name===e.target.value);replaceChoices($("#byom-reference",form),["(Automatic)",...(c?.values||[])],"(Automatic)");});
  $("#byom-truth",form).addEventListener("change",(e)=>{const c=columns.find(x=>x.name===e.target.value);replaceChoices($("#byom-truth-positive",form),c?.values||[],suggested.truth_positive_value);});
  const auditBtn=button("Run group comparison",async()=>{try{
    const decision=$("#byom-decision").value, group=$("#byom-group").value, truth=$("#byom-truth").value;
    const decisionInfo=columns.find(c=>c.name===decision), body={upload_id:byomUpload.upload_id,decision_column:decision,group_column:group};
    if(truth!=="(No actual outcomes)"){body.truth_column=truth;body.truth_positive_value=$("#byom-truth-positive").value||undefined;}
    if(decisionInfo?.numeric&&decisionInfo.n_unique>2){const t=$("#byom-threshold").value;if(t!=="")body.threshold=Number(t);}
    else {const favorable=$("#byom-favorable").value;if(favorable)body.favorable_value=favorable;}
    const reference=$("#byom-reference").value;if(reference!=="(Automatic)")body.reference_group=reference;
    byomResult=await api.byomAudit(body);renderByom(title,intro);
  }catch(e){renderError(title,intro,e);}},"primary");
  const resultPanel=byomResult?h("section",{class:"card byom-results"},h("h2","Group comparison"),h("p",byomResult.mode==="score"?`Numeric score converted to a favorable decision at cutoff ${displayValue(byomResult.threshold_used)}.`:"Favorable label selected from the decision column."),
    h("div",{class:"reading-guide"},h("strong","Interpret the result carefully"),h("p",`The comparison uses ${byomResult.n_rows.toLocaleString()} rows. Groups under ${byomResult.small_group_limit} rows are flagged as small. The four-fifths threshold is a screening heuristic, not a legal test or proof of discrimination.`)),
    (byomResult.findings||[]).map((f)=>h("p",{class:"finding-line"},f.replaceAll("**",""))),
    table(byomResult.table||[],Object.keys(byomResult.table?.[0]||{}).map(k=>[k,nice(k)]))):null;
  shell(title,intro,h("div",{class:"byom-page"},uploadPanel,
    h("section",{class:"card"},h("h2","Tell FairLens how to read the columns"),h("p","Choose the model’s decision, the group to compare, and an actual outcome column if one exists."),form,h("div",{class:"row"},auditBtn)),
    resultPanel,
    h("details",{class:"result-details"},h("summary","Column preview"),table(columns.map((c)=>({name:c.name,type:c.numeric?"Numeric":"Category",unique:c.n_unique,example_values:(c.values||[]).slice(0,6).join(", ")})),[["name","Column"],["type","Type"],["unique","Distinct values"],["example_values","Example values"]]))
  ));
}
function valueView(key,value,depth=0) {
  if (value == null || typeof value !== "object") return h("div",{class:"detail-pair"},h("dt",nice(key)),h("dd",displayValue(value)));
  if (Array.isArray(value)) {
    if (!value.length) return h("p",{class:"muted"},"No records returned.");
    if (value.every((v)=>v && typeof v==="object" && !Array.isArray(v))) {
      const keys=[...new Set(value.flatMap((r)=>Object.keys(r)))];
      const content=table(value,keys.map((k)=>[k,nice(k)]));
      return value.length>10?h("details",{class:"result-details"},h("summary",`Show ${value.length.toLocaleString()} records`),content):content;
    }
    return h("ul",{class:"plain-list"},value.map((v)=>h("li",displayValue(v))));
  }
  const entries=Object.entries(value);
  if (depth>1) return h("details",{class:"result-details"},h("summary",nice(key)),h("pre",{class:"json-view"},JSON.stringify(value,null,2)));
  const simple=entries.filter(([,v])=>v==null||typeof v!=="object");
  const complex=entries.filter(([,v])=>v!=null&&typeof v==="object");
  return h("div",{},simple.length&&h("dl",{class:"detail-grid"},simple.map(([k,v])=>valueView(k,v,depth+1))),complex.map(([k,v])=>h("section",{class:"nested-result"},h("h3",nice(k)),valueView(k,v,depth+1))));
}
const pageGuidance={
  data:"The UCI benchmark contains historical records; Synthetic demo uses invented records. Always check the source label before interpreting a result.",
  evaluation:"These model comparisons use the validation split. Compare the error types and cost as well as the summary metrics; do not treat a single score as a fairness verdict.",
  groups:"Rates are shown with group counts and uncertainty where available. Small denominators make estimates less stable; a group gap is a prompt to investigate, not a causal conclusion.",
  experiment:"Explore thresholds on validation data. Pin a configuration only when ready: that runs and freezes the one final test review for this browser session.",
  report:"The report uses the pinned final test review. It preserves the evaluation context, group counts, uncertainty, and limitations.",
  map:"Dots are applicants positioned by similarity across non-sensitive inputs. Terrain is shown only for regions with enough applicants in both age groups.",
  proxies:"Proxy detection measures predictive association in this dataset. It does not establish intent, causation, or legal discrimination.",
  mitigation:"Mitigation results are experiments on this benchmark. Compare the full cost and group outcome trade-offs; no strategy guarantees fairness.",
  byom:"Your upload is held in memory for this browser session. Confirm the decision and group columns before interpreting group rates.",
  methodology:"Definitions and assumptions determine how to read every metric. Review the limitations alongside measured results.",
};
function renderPage(title, intro, data) {
  const action = current === "experiment" ? h("section", { class: "experiment-actions" },
      h("div",{},h("div",{class:"eyebrow"},"VALIDATION SET ONLY"),h("h2","Choose the decision threshold"),h("p","This changes the probability cutoff used to classify an applicant as Good. Explore here before pinning the final test review.")),
      h("label",{class:"threshold-control"},h("span","Good-risk probability cutoff"),h("div",{class:"range-row"},h("input",{type:"range",min:0.05,max:0.95,step:0.01,value:store.get().rule?.threshold??0.5,oninput:(e)=>{$("#threshold-value").textContent=`${Math.round(Number(e.target.value)*100)}%`;},onchange:(e)=>store.set({rule:{mode:"single",threshold:Number(e.target.value),tYoung:Number(e.target.value),tOld:Number(e.target.value)}})}),h("output",{id:"threshold-value"},`${Math.round((store.get().rule?.threshold??0.5)*100)}%`))),
      button("Pin final test review", async () => { try { const result = await api.pin(body()); renderPage("Final review pinned", "The test set is now frozen for this browser session.", result); } catch (e) { renderError(title, intro, e); } }, "primary"))
    : current === "report" ? h("div", { class: "row section" },
      button("Download Markdown report", async () => { try { const md = await api.reportMarkdown(); const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([md], {type:"text/markdown"})); a.download="fairlens_report.md"; a.click(); URL.revokeObjectURL(a.href); } catch (e) { renderError(title, intro, e); } }, "primary"))
    : current === "data" && store.get().source === "real" && data.benchmark_available === false ? h("div", { class: "row section" },
      button("Download UCI benchmark", async () => { try { await api.downloadData(); await route(); } catch (e) { renderError(title, intro, e); } }, "primary"))
    : null;
  const skipped=["data_source","settings"], simple=Object.entries(data).filter(([k,v])=>!skipped.includes(k)&&(v==null||typeof v!=="object"));
  const structured=Object.entries(data).filter(([k,v])=>!skipped.includes(k)&&v!=null&&typeof v==="object");
  const source=data.data_source;
  const sourceLabel=source?.synthetic||store.get().source==="demo"?"Synthetic demo data · invented records":source?.label||"UCI German Credit benchmark";
  const overview=data.data_source&&typeof data.data_source==="string";
  const startGuide=overview?h("section",{class:"start-guide"},
    h("div",{class:"start-copy"},h("div",{class:"eyebrow"},"A CLEAR PATH THROUGH THE AUDIT"),h("h2","Start with the evidence. Then explore the trade-offs."),h("p","FairLens is an educational review of a historical credit-risk model. Follow these steps to keep validation experiments separate from the final test review.")),
    h("div",{class:"start-steps"},[
      ["01","Choose a data source","Use the UCI benchmark when available, or switch to clearly labeled synthetic demo data."],
      ["02","Review model results","Compare errors, costs, group rates, and sample counts on validation data."],
      ["03","Explore and report","Test what-ifs, then pin one configuration before opening the final test report."],
    ].map(([n,t,d],i)=>h("a",{class:"start-step",href:["#data","#evaluation","#experiment"][i]},h("span",{class:"step-number"},n),h("strong",t),h("p",d),h("span",{class:"step-link"},"Open step →"))))
  ):null;
  const content=h("div",{class:"result-page"},
    (source||store.get().source)&&h("div",{class:`source-banner ${source?.synthetic||store.get().source==="demo"?"demo":""}`},h("strong",sourceLabel),source?.notice&&h("span",source.notice)),
    startGuide,
    pageGuidance[current]&&h("aside",{class:"reading-guide"},h("strong","How to read this page"),h("p",pageGuidance[current])),
    current==="overview"&&data.benchmark_available===false&&h("aside",{class:"next-step-card"},h("strong","The real benchmark is not installed on this server yet."),h("p","You can download the UCI dataset on the Data page, or switch to Synthetic demo data to explore the interface with clearly labeled invented records."),button("Explore synthetic demo",()=>store.set({source:"demo"}),"primary")),
    action,
    simple.length&&h("section",{class:"summary-panel"},h("h2",overview?"System and data status":"Key results"),h("dl",{class:"summary-grid"},simple.map(([k,v])=>valueView(k,v)))),
    structured.map(([k,v])=>card(nice(k),valueView(k,v),"RESULT DETAILS")),
    data.settings&&h("details",{class:"result-details context-details"},h("summary","Analysis settings used for these results"),valueView("settings",data.settings)),
    h("details",{class:"result-details raw-details"},h("summary","Technical detail · complete API response"),h("pre",{class:"json-view"},JSON.stringify(data,null,2)))
  );
  shell(title, intro, content);
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
  if (current === "methodology") return load(title,intro,async()=>{const [methods,glossary]=await Promise.all([api.methodology(src),api.meta()]);return {...methods,metric_definitions:glossary.metric_help,feature_definitions:glossary.features,costs:methods.costs,split:glossary.split};});
  if (current === "map") { if(!meta) { try { meta=await api.meta(); } catch {} } await renderApplicantMap(title,intro); return; }
  if (current === "simulator") { try { const schema=await api.simSchema(src); renderSimulator(title,intro,schema); } catch(e) { renderError(title,intro,e); } return; }
  if (current === "proxies") return load(title,intro,()=>api.proxyReport({source:src}));
  if (current === "mitigation") return load(title,intro,()=>api.mitigation({source:src,model:store.get().model}));
  if (current === "byom") return renderByom(title,intro);
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
