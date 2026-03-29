"""Sanity checks for ``docs/Packaging.md`` and ``docs/customer/README.md``."""

from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS = _REPO_ROOT / "docs"
PACKAGING = DOCS / "Packaging.md"
CUSTOMER_README = DOCS / "customer" / "README.md"


def _assert_md_links_resolve(base: Path, text: str) -> None:
    for raw in re.findall(r"\]\(([^)]+\.md)\)", text):
        target = (base / raw.split("#", 1)[0]).resolve()
        assert target.is_file(), f"broken link {raw!r} from {base} → {target}"


def test_packaging_md_exists_and_links() -> None:
    assert PACKAGING.is_file()
    text = PACKAGING.read_text(encoding="utf-8")
    _assert_md_links_resolve(DOCS, text)
    assert "A2.1" in text and "docker build" in text
    assert "python -m build" in text


def test_customer_readme_exists_and_links() -> None:
    assert CUSTOMER_README.is_file()
    text = CUSTOMER_README.read_text(encoding="utf-8")
    _assert_md_links_resolve(CUSTOMER_README.parent, text)
