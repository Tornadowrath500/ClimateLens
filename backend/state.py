"""Server-side state that replaces Streamlit's session_state and @st.cache_* decorators.

* Dataset + fitted-audit caches (shared; keyed by data source, so a replaced file is re-read).
* Per-browser-tab sessions identified by the X-FairLens-Session header: the pinned final test review
  (once per session, frozen) and in-memory uploads. Nothing here is ever written to disk.
"""

from __future__ import annotations

import re
import threading
import time
from collections import OrderedDict

import pandas as pd

from backend.errors import ServiceError
from fairlens.config import RANDOM_STATE, dataset_path
from fairlens.data import load_dataset
from fairlens.demo import make_demo_dataset
from fairlens.evaluation import Audit, run_audit

SOURCES = ("real", "demo")
_cache_lock = threading.RLock()
_build_lock = threading.RLock()  # one expensive build (model training) at a time
_datasets: OrderedDict = OrderedDict()
_audits: OrderedDict = OrderedDict()
_derived: OrderedDict = OrderedDict()  # maps, proxy reports, mitigation tables
_sessions: OrderedDict = OrderedDict()
MAX_AUDITS, MAX_DERIVED, MAX_DATASETS, MAX_SESSIONS, MAX_UPLOADS_PER_SESSION = 8, 24, 4, 500, 5
SESSION_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def cached(cache: OrderedDict, key, builder, limit: int):
    """Return cache[key], building it once (serialised) when absent."""
    with _cache_lock:
        if key in cache:
            cache.move_to_end(key)
            return cache[key]
    with _build_lock:
        with _cache_lock:
            if key in cache:
                cache.move_to_end(key)
                return cache[key]
        value = builder()
        with _cache_lock:
            cache[key] = value
            while len(cache) > limit:
                cache.popitem(last=False)
        return value


def clear_caches() -> None:
    with _cache_lock:
        _datasets.clear(), _audits.clear(), _derived.clear()


# ---- data -------------------------------------------------------------------------------------
def real_dataset_available() -> bool:
    return dataset_path().exists()


def dataset_key(source: str) -> tuple:
    if source == "demo":
        return ("demo",)
    if source == "real":
        path = dataset_path()
        if not path.exists():
            raise ServiceError(
                409, "dataset_missing",
                "The dataset is not on this server yet. Download the UCI file once, or explore with the synthetic demo data.",
                {"can_download": True, "demo_available": True},
            )
        return ("real", str(path), path.stat().st_mtime)
    raise ServiceError(422, "invalid_source", "source must be 'real' or 'demo'.", {"allowed": list(SOURCES)})


def get_dataset(source: str) -> tuple[pd.DataFrame, tuple]:
    """The validated dataset. Treat the returned frame as read-only: it is shared between requests."""
    key = dataset_key(source)

    def build() -> pd.DataFrame:
        if source == "demo":
            return make_demo_dataset()
        try:
            return load_dataset(dataset_path())
        except (ValueError, TypeError) as exc:  # schema problems: messages never contain filesystem paths
            raise ServiceError(422, "dataset_invalid", f"The dataset could not be validated: {exc}") from exc
        except Exception as exc:
            raise ServiceError(422, "dataset_invalid", "The dataset file could not be read.") from exc

    return cached(_datasets, key, build, MAX_DATASETS), key


def get_audit(source: str, excluded: tuple[str, ...]) -> tuple[Audit, tuple]:
    data, dkey = get_dataset(source)
    key = (dkey, tuple(excluded), RANDOM_STATE)
    return cached(_audits, key, lambda: run_audit(data, excluded=tuple(excluded), seed=RANDOM_STATE), MAX_AUDITS), key


def derived(key: tuple, builder):
    return cached(_derived, key, builder, MAX_DERIVED)


# ---- sessions ---------------------------------------------------------------------------------
def get_session(session_id: str | None) -> dict:
    if not session_id or not SESSION_RE.match(session_id):
        raise ServiceError(
            400, "invalid_session",
            "Send a session id of 8-64 letters, digits, '-' or '_' in the X-FairLens-Session header.",
        )
    with _cache_lock:
        if session_id not in _sessions:
            _sessions[session_id] = {"lock": threading.RLock(), "pinned": None, "uploads": OrderedDict()}
            while len(_sessions) > MAX_SESSIONS:
                _sessions.popitem(last=False)
        _sessions.move_to_end(session_id)
        return _sessions[session_id]


def add_upload(session_id: str | None, upload_id: str, record: dict) -> None:
    session = get_session(session_id)
    with session["lock"]:
        session["uploads"][upload_id] = {**record, "created": time.time()}
        while len(session["uploads"]) > MAX_UPLOADS_PER_SESSION:
            session["uploads"].popitem(last=False)


def get_upload(session_id: str | None, upload_id: str) -> dict:
    session = get_session(session_id)
    with session["lock"]:
        record = session["uploads"].get(upload_id)
    if record is None:
        raise ServiceError(404, "upload_not_found", "That upload is not available in this session. Upload the file again.")
    return record