from __future__ import annotations

import ast
import os
from typing import List, Dict, Any

from core.models import Task


# ============================================================
#  Context Limits (v3)
# ============================================================

CONTEXT_LIMITS = {
    "max_files": 8,
    "max_lines_per_file": 300,
    "max_total_lines": 1500,
    "context_window": 40,
}


# ============================================================
#  1. Import-Analyse (Dependency Graph)
# ============================================================

def extract_imports(source: str) -> List[str]:
    """
    Extracts imported module names from a Python file.
    Used for dependency scoring.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split(".")[0])

    return imports


# ============================================================
#  2. Flask Awareness
# ============================================================

def detect_flask_relevance(source: str) -> bool:
    """
    Detects Flask-relevant files:
    - @app.route
    - Blueprint(...)
    - render_template
    - request/session/g
    """
    flask_markers = [
        "@app.route",
        "Blueprint(",
        "render_template(",
        "request",
        "session",
        "g.",
    ]
    return any(marker in source for marker in flask_markers)


# ============================================================
#  3. AST-basierte Funktions-Extraktion
# ============================================================

def extract_function_snippet(source: str, func_name: str) -> str:
    """
    Extracts a function with context window.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ""

    lines = source.splitlines()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            start = max(node.lineno - 1 - CONTEXT_LIMITS["context_window"], 0)
            end = min(node.end_lineno + CONTEXT_LIMITS["context_window"], len(lines))
            return "\n".join(lines[start:end])

    return ""


# ============================================================
#  4. Relevante Snippets (v3)
# ============================================================

def extract_relevant_snippets(path: str) -> str:
    """
    Extracts relevant code snippets for LLM context.
    Flask files → full file (bounded)
    Normal modules → top-level functions/classes
    """

    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    # Flask files → full file (bounded)
    if detect_flask_relevance(source):
        lines = source.splitlines()
        return "\n".join(lines[:CONTEXT_LIMITS["max_lines_per_file"]])

    # Normal modules → extract definitions
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source[:CONTEXT_LIMITS["max_lines_per_file"]]

    lines = source.splitlines()
    snippets = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            start = max(node.lineno - 1, 0)
            end = node.end_lineno
            snippet = "\n".join(lines[start:end])
            snippets.append(snippet)

    if not snippets:
        return source[:CONTEXT_LIMITS["max_lines_per_file"]]

    return "\n\n".join(snippets)


# ============================================================
#  5. File Scoring (v3)
# ============================================================

def score_file(task: Task, spec_profile: Dict[str, Any], file_meta: Dict[str, Any]) -> int:
    score = 0

    # 1. Target module priority
    if file_meta["module"] == task.module:
        score += 5

    # 2. Import relationship
    if file_meta.get("is_imported_by_target"):
        score += 4

    # 3. Pattern match
    if file_meta.get("matches_pattern"):
        score += 2

    # 4. Flask relevance
    full_path = file_meta["path"]
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            source = f.read()
        if detect_flask_relevance(source):
            score += 6
    except Exception:
        pass

    # 5. Recently used
    if file_meta.get("used_in_last_runs"):
        score += 1

    return score


def _sort_key(scored: tuple) -> tuple:
    score, meta = scored
    return (-score, meta["line_count"], meta["import_count"], meta["path"])


def select_files_for_task(task: Task, spec_profile: Dict[str, Any], file_metas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    scored = [(score_file(task, spec_profile, meta), meta) for meta in file_metas]
    scored.sort(key=_sort_key)
    return [meta for _, meta in scored[:CONTEXT_LIMITS["max_files"]]]


# ============================================================
#  6. Snippet Loader (LLM-safe)
# ============================================================

def load_snippets(selected_files: List[Dict[str, Any]], root: str) -> Dict[str, Any]:
    """
    Loads reduced snippets for each selected file.
    Flask files → full file (bounded)
    Helpers → snippets
    """

    max_total_lines = CONTEXT_LIMITS["max_total_lines"]
    result = []
    total_lines = 0

    for meta in selected_files:
        if total_lines >= max_total_lines:
            break

        full_path = os.path.join(root, meta["path"])

        with open(full_path, "r", encoding="utf-8") as f:
            source = f.read()

        # Flask files → full file (bounded)
        if detect_flask_relevance(source):
            snippet_lines = source.splitlines()
        else:
            snippet = extract_relevant_snippets(full_path)
            snippet_lines = snippet.splitlines()

        remaining = max_total_lines - total_lines
        allowed = min(len(snippet_lines), remaining)

        reduced = "\n".join(snippet_lines[:allowed])

        result.append({
            "path": meta["path"],
            "content": reduced
        })

        total_lines += allowed

    return {"files": result}
