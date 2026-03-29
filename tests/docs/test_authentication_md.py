"""Sanity checks for ``docs/Authentication.md``."""

from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS = _REPO_ROOT / "docs"
AUTH_DOC = DOCS / "Authentication.md"


def test_authentication_md_exists() -> None:
    assert AUTH_DOC.is_file(), f"expected {AUTH_DOC}"


def test_authentication_md_internal_md_links_resolve() -> None:
    text = AUTH_DOC.read_text(encoding="utf-8")
    for raw in re.findall(r"\]\(([^)]+\.md)\)", text):
        path = (DOCS / raw.split("#", 1)[0]).resolve()
        assert path.is_file(), f"broken link target {raw!r} (resolved {path})"


def test_authentication_md_mentions_launch_check_vars() -> None:
    text = AUTH_DOC.read_text(encoding="utf-8")
    assert "AUTH0_SECRET" in text
    assert "NEXT_PUBLIC_SUPABASE_URL" in text
    assert "X-API-Key" in text
