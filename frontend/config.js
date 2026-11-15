/* Runtime configuration. Edit this file (or override with ?api=http://host:port) instead of touching app code.
 *
 * apiBase "" means "same origin": use it when FastAPI serves this folder (uvicorn backend.main:app).
 * When the frontend is served separately on port 5173 (see README), the API is assumed at localhost:8000.
 */
window.FAIRLENS_CONFIG = {
  apiBase: new URLSearchParams(location.search).get("api") || (location.port === "5173" ? "http://localhost:8000" : ""),
};
