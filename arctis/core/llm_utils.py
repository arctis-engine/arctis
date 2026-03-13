from __future__ import annotations

import re
from typing import Optional


# ============================================================
#  v3 Codeblock Extractor (deterministic, safe)
# ============================================================

CODEBLOCK_PATTERN = re.compile(
    r"```(?:[a-zA-Z0-9_+-]+)?\s*\n(.*?)```",
    re.DOTALL
)

INLINE_CODE_PATTERN = re.compile(
    r"`([^`]+)`"
)


def extract_code_block(text: str) -> str:
    """
    Arctic Brain v3:
    - erkennt Markdown-Codeblöcke
    - erkennt Inline-Codeblöcke
    - deterministisch
    - niemals destruktiv
    - niemals aggressive Extraktion
    - Fallback: Originaltext

    Regeln:
    1. Wenn ein Markdown-Codeblock existiert → nimm den ersten.
    2. Sonst, wenn Inline-Code existiert → nimm den ersten Inline-Code.
    3. Sonst → gib den Originaltext zurück.
    """

    if not text:
        return ""

    # ------------------------------------------------------------
    # 1. Markdown-Codeblock
    # ------------------------------------------------------------
    match = CODEBLOCK_PATTERN.search(text)
    if match:
        content = match.group(1).strip()
        if content:
            return content

    # ------------------------------------------------------------
    # 2. Inline-Codeblock
    # ------------------------------------------------------------
    inline = INLINE_CODE_PATTERN.search(text)
    if inline:
        content = inline.group(1).strip()
        if content:
            return content

    # ------------------------------------------------------------
    # 3. Fallback: Originaltext
    # ------------------------------------------------------------
    return text.strip()
