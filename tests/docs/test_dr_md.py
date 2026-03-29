"""Sanity checks for ``docs/DR.md``."""

from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS = _REPO_ROOT / "docs"
DR_DOC = DOCS / "DR.md"


def test_dr_md_exists() -> None:
    assert DR_DOC.is_file(), f"expected {DR_DOC}"


def test_dr_md_internal_md_links_resolve() -> None:
    text = DR_DOC.read_text(encoding="utf-8")
    for raw in re.findall(r"\]\(([^)]+\.md)\)", text):
        path = (DOCS / raw.split("#", 1)[0]).resolve()
        assert path.is_file(), f"broken link target {raw!r} (resolved {path})"


def test_dr_md_mentions_a15_backup_and_verification() -> None:
    text = DR_DOC.read_text(encoding="utf-8")
    assert "A1.5" in text or "Backup jobs" in text
    assert "Verification" in text
