/* The ONLY module that talks to the backend. Pages call these named functions; nothing else uses fetch().
 * Contract: docs/API.md and the live OpenAPI at <apiBase>/api/docs. Backend errors always look like
 * {"error": {"code", "message", "details"}} and are thrown here as ApiError. */

import { sessionId } from "./store.js";

const BASE = (window.FAIRLENS_CONFIG?.apiBase || "").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(status, code, message, details = {}) { super(message); this.name = "ApiError"; this.status = status; this.code = code; this.details = details; }
}

async function request(method, path, { body, query, signal, form, text } = {}) {
  const url = new URL(`${BASE}/api${path}`, location.href);
  for (const [k, v] of Object.entries(query || {})) if (v != null) url.searchParams.set(k, v);
  const headers = { "X-FairLens-Session": sessionId() };
  const init = { method, headers, signal };
  if (form) init.body = form;
  else if (body !== undefined) { headers["Content-Type"] = "application/json"; init.body = JSON.stringify(body); }
  let res;
  try { res = await fetch(url, init); }
  catch (e) {
    if (e.name === "AbortError") throw e;
    throw new ApiError(0, "network_error", "Can't reach the FairLens server. Check that the backend is running (see README).");
  }
  if (!res.ok) {
    let err = {};
    try { err = (await res.json()).error || {}; } catch { /* non-JSON error body */ }
    throw new ApiError(res.status, err.code || "http_error", err.message || `The server answered ${res.status}.`, err.details);
  }
  return text ? res.text() : res.json();
}
const get = (path, query, o) => request("GET", path, { query, ...o });
const post = (path, body, o) => request("POST", path, { body, ...o });

export const api = {
  // system
  health: (o) => get("/health", null, o),
  meta: (o) => get("/meta", null, o),
  methodology: (source, o) => get("/methodology", { source }, o),
  // data
  dataStatus: (o) => get("/data/status", null, o),
  downloadData: (o) => post("/data/download", {}, o),
  dataOverview: (source, o) => get("/data/overview", { source }, o),
  // evaluation and group outcomes
  evaluation: (body, o) => post("/evaluation/validation", body, o),
  groupsReview: (body, o) => post("/groups/review", body, o),
  groupsStability: (body, o) => post("/groups/stability", body, o),
  // experiment lab and report
  sweep: (body, o) => post("/experiment/sweep", body, o),
  pin: (body, o) => post("/experiment/pin", body, o),
  pinned: (o) => get("/experiment/pin", null, o),
  findings: (o) => get("/report/findings", null, o),
  reportMarkdown: (o) => request("GET", "/report/markdown", { text: true, ...o }),
  // applicants
  map: (body, o) => post("/map", body, o),
  mapApplicant: (body, o) => post("/map/applicant", body, o),
  simSchema: (source, o) => get("/simulator/schema", { source }, o),
  simRandom: (source, o) => post("/simulator/random", { source }, o),
  simEvaluate: (body, o) => post("/simulator/evaluate", body, o),
  // fairness tools
  proxyReport: (body, o) => post("/proxies/report", body, o),
  proxyRemoval: (body, o) => post("/proxies/removal", body, o),
  mitigation: (body, o) => post("/mitigation/run", body, o),
  // audit your own model
  byomUpload: (file, o) => { const form = new FormData(); form.append("file", file); return request("POST", "/byom/upload", { form, ...o }); },
  byomSample: (body, o) => post("/byom/sample", body, o),
  byomAudit: (body, o) => post("/byom/audit", body, o),
};