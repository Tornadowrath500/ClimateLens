# FairLens API contract

HTTP routes live in `backend/api/`, request validation in `backend/schemas.py`,
and framework independent behavior in `backend/services/`. These adapters
reuse the existing implementation in `src/fairlens/`. OpenAPI is at
`/api/openapi.json`; interactive documentation is at `/api/docs`.

JSON errors use `{"error":{"code":"...","message":"...","details":{}}}`.
Missing real data returns HTTP 409 with `dataset_missing`; the UCI benchmark is
never downloaded automatically. Use `source=demo` to explore synthetic data.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Liveness and version |
| GET | `/api/meta` | Feature labels, model names, metric definitions |
| GET | `/api/methodology?source=real\|demo` | Methodology and limitations |
| GET | `/api/data/status` | Benchmark availability |
| POST | `/api/data/download` | Explicit benchmark download |
| GET | `/api/data/overview?source=real\|demo` | Dataset overview |
| POST | `/api/evaluation/validation` | Model and baseline comparison |
| POST | `/api/groups/review` | Group rates and uncertainty |
| POST | `/api/groups/stability` | Repeated split sensitivity |
| POST | `/api/experiment/sweep` | Validation threshold analysis |
| POST | `/api/experiment/pin` | Pin one final test review per session |
| GET | `/api/experiment/pin` | Read the pinned review |
| GET | `/api/report/findings` | Findings from the pinned review |
| GET | `/api/report/markdown` | Download the report |
| POST | `/api/map` | Applicant map and group terrain |
| POST | `/api/map/applicant` | Applicant explanation and what-if path |
| GET | `/api/simulator/schema?source=real\|demo` | Simulator feature schema |
| POST | `/api/simulator/random` | Sample a training profile |
| POST | `/api/simulator/evaluate` | Evaluate a supplied profile |
| POST | `/api/proxies/report` | Proxy detection |
| POST | `/api/proxies/removal` | Sensitive input removal comparison |
| POST | `/api/mitigation/run` | Compare mitigation strategies |
| POST | `/api/byom/upload` | Upload a bounded CSV for this session |
| POST | `/api/byom/sample` | Create a sample FairLens prediction upload |
| POST | `/api/byom/audit` | Audit uploaded decisions by group |

Analysis requests generally accept `source` (`real` or `demo`), `model`
(`Logistic regression` or `Random forest`), and `excluded` (currently age
`Attribute13` and/or status/sex `Attribute9`). Decision requests accept a
0–1 threshold and optional group thresholds. Schemas reject unknown fields.
Uploads and session identifiers are validated server-side.

The centralized JavaScript request layer is `frontend/api.js`; frontend pages
should call it instead of making direct `fetch` requests. The per-tab
`X-FairLens-Session` header scopes uploads and the one-time final review.

## Local development

From the repository root, run `uvicorn backend.main:app --reload`. FastAPI
serves the frontend at `/`. Set `FAIRLENS_SERVE_FRONTEND=0` to use a separate
static server; configure `FAIRLENS_CORS_ORIGINS` with its allowed origins.
