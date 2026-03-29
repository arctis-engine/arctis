"""Sanity checks for ``docs/commercial/*.md`` link targets."""

from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS = _REPO_ROOT / "docs"
COMMERCIAL = DOCS / "commercial"


def test_commercial_docs_exist() -> None:
    assert (COMMERCIAL / "README.md").is_file()
    for name in (
        "pricing_and_limits.md",
        "sla_and_support.md",
        "evidence_bundle.md",
        "release_notes.md",
        "COMMERCIAL_CHECKLIST.md",
    ):
        assert (COMMERCIAL / name).is_file(), f"missing {name}"


def test_commercial_md_links_resolve() -> None:
    for md_path in sorted(COMMERCIAL.glob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        base = md_path.parent
        for raw in re.findall(r"\]\(([^)]+\.md)\)", text):
            target = (base / raw.split("#", 1)[0]).resolve()
            assert target.is_file(), f"broken {raw!r} in {md_path.name} → {target}"
