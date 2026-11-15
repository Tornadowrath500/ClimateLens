"""Dataset status, explicit download, and the data-overview page."""

from __future__ import annotations

from backend import state
from backend.errors import ServiceError
from backend.services.common import respond, source_info
from fairlens.config import AGE_COLUMN, AGE_GROUP_CUTOFF, TARGET_COLUMN, dataset_path
from fairlens.data import benchmark_shape_warnings, dataset_provenance, download_dataset, make_age_groups
from fairlens.metrics import wilson_interval


def data_status() -> dict:
    """Is the real benchmark on the server? Never reveals filesystem paths."""
    available = state.real_dataset_available()
    return respond(source_info("real"), {
        "real_available": available, "demo_available": True,
        "provenance": dataset_provenance() if available else {},
    })


def data_download() -> dict:
    """Explicit, user-triggered download of the UCI benchmark to the server's data directory."""
    try:
        download_dataset(output_path=dataset_path())
    except ImportError as exc:
        raise ServiceError(501, "download_unavailable",
                           "The 'ucimlrepo' package is not installed on the server. Run python scripts/download_dataset.py "
                           "after installing it, or use the synthetic demo data.") from exc
    except Exception as exc:  # network, package or schema problems
        raise ServiceError(502, "download_failed", f"The download failed: {str(exc)[:300]}",
                           {"manual_url": "https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data"}) from exc
    state.clear_caches()
    return data_status()


def data_overview(source: str = "real") -> dict:
    data, _ = state.get_dataset(source)
    info = source_info(source)
    n, bad = len(data), int((data[TARGET_COLUMN] == 2).sum())
    labels = make_age_groups(data[AGE_COLUMN])
    groups = []
    for name in sorted(labels.unique(), reverse=True):
        part = data[labels == name]
        k = int((part[TARGET_COLUMN] == 2).sum())
        lo, hi = wilson_interval(k, len(part))
        groups.append({"name": name, "n": len(part), "n_bad": k, "bad_share": k / len(part), "ci_low": lo, "ci_high": hi})
    manifest, warnings = {}, []
    if source == "real":
        manifest = dataset_provenance()
        warnings = benchmark_shape_warnings(data)
        if not manifest:
            warnings.append("No download manifest found, so the file's origin is unverified.")
    return respond(info, {
        "n": n, "n_features": data.shape[1] - 1, "n_bad": bad, "bad_share": bad / n,
        "cutoff": AGE_GROUP_CUTOFF, "groups": groups,
        "head": data.head(10),
        "provenance": {"manifest": manifest, "warnings": warnings, "retrieved": str(manifest.get("retrieved_utc", ""))[:10] or None},
    })
