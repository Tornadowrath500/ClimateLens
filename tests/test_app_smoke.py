
"""Render every page through the actual multipage Streamlit app.

Uses synthetic data via FAIRLENS_DATA_PATH, so it needs no network.
"""

from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    "app.py",
    "pages/1_Understand_the_Data.py",
    "pages/2_Evaluate_the_Model.py",
    "pages/3_Investigate_Group_Outcomes.py",
    "pages/4_Experiment_Lab.py",
    "pages/5_Findings_and_Report.py",
    "pages/6_Methodology_and_Limitations.py",
    "pages/7_Applicant_Map.py",
    "pages/8_Applicant_Simulator.py",
    "pages/9_Proxy_Detector.py",
    "pages/10_Mitigation_Lab.py",
    "pages/11_Audit_Your_Model.py",
]


@pytest.mark.parametrize("page", PAGES)
def test_page_renders_without_exception(page, synthetic_csv, monkeypatch):
    monkeypatch.setenv("FAIRLENS_DATA_PATH", str(synthetic_csv))

    # Launch the real entrypoint so Streamlit registers its pages.
    at = AppTest.from_file(
        str(ROOT / "app.py"),
        default_timeout=180,
    ).run()

    # Navigate to the requested page within the registered app.
    if page != "app.py":
        at.switch_page(page).run()

    assert not at.exception, [e.value for e in at.exception]


def test_missing_dataset_offers_explicit_download_instead_of_crashing(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("FAIRLENS_DATA_PATH", str(tmp_path / "absent.csv"))

    at = AppTest.from_file(
        str(ROOT / "pages/2_Evaluate_the_Model.py"),
        default_timeout=60,
    ).run()

    assert not at.exception
    assert any("Download the dataset" in b.label for b in at.button)
