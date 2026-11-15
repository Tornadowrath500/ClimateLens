"""Keep the navigation, quick-jump list and page files in sync."""

import re
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from fairlens.ui import JUMP  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
NAV = set(re.findall(r'st\.Page\("(pages/[^"]+\.py)"', (ROOT / "app.py").read_text(encoding="utf-8")))


def test_every_navigation_target_exists():
    assert NAV, "no pages found in app.py"
    assert all((ROOT / path).is_file() for path in NAV)


def test_every_page_file_is_reachable_from_navigation():
    pages = {f"pages/{p.name}" for p in (ROOT / "pages").glob("*.py")}
    assert pages == NAV, f"orphaned or missing: {sorted(pages ^ NAV)}"


def test_quick_jump_matches_navigation():
    assert {path for _, path in JUMP} == NAV
    assert len({title for title, _ in JUMP}) == len(JUMP)


def test_every_page_title_has_breadcrumb_metadata():
    from fairlens.ui import PAGE_META

    titles = set()
    for path in NAV:
        match = re.search(r'setup_page\("([^"]+)"\)', (ROOT / path).read_text(encoding="utf-8"))
        assert match, f"{path} does not call setup_page"
        titles.add(match.group(1))
    assert titles - {"Home"} == set(PAGE_META), sorted(titles ^ set(PAGE_META))

