from __future__ import annotations

from typing import Dict, Any
from core.models import Task


# ============================================================
#  Helper: Format dicts deterministically
# ============================================================

def _fmt_block(d: Dict[str, Any]) -> str:
    if not isinstance(d, dict) or not d:
        return "none"
    parts = [f"{k}={v}" for k, v in sorted(d.items())]
    return "; ".join(parts)


# ============================================================
#  System Prompt (v3)
# ============================================================

def build_system_prompt(spec_profile: Dict[str, Any]) -> str:
    """
    v3 system prompt:
    - deterministic
    - architecture-driven
    - strictly code-only
    - spec-aware
    """

    effective = spec_profile.get("effective", {})

    naming = effective.get("naming", {})
    allowed_ops = effective.get("allowed_operations", {})
    style = effective.get("style", {})
    structure = effective.get("structure", {})
    forbidden = effective.get("forbidden", {})

    return (
        "You are Arctic Brain v3, a deterministic architecture-driven code generator. "
        "You output ONLY valid Python code. "
        "No explanations. No markdown. No backticks. "
        "No comments except docstrings. "
        "Start directly with the first line of code. "
        "Follow all rules strictly. "
        f"Naming rules: {_fmt_block(naming)}. "
        f"Allowed operations: {_fmt_block(allowed_ops)}. "
        f"Style rules: {_fmt_block(style)}. "
        f"Structure rules: {_fmt_block(structure)}. "
        f"Forbidden: {_fmt_block(forbidden)}. "
        "Never output placeholders, TODOs, or unused helpers. "
        "Never output analysis or reasoning. "
        "Only final code."
    )


# ============================================================
#  User Prompt (v3)
# ============================================================

def build_user_prompt(task: Task, ctx: Dict[str, Any], spec_profile: Dict[str, Any]) -> str:
    """
    v3 user prompt:
    - task-aware
    - context-aware
    - deterministic
    - code-only instruction
    """

    # Context assembly
    context_parts = []
    for f in ctx.get("files", []):
        path = f.get("path", "")
        content = f.get("content", "")
        context_parts.append(f"FILE {path}:\n{content}")

    context_block = "\n\n".join(context_parts) if context_parts else "No context."

    return (
        f"Task: {task.name}. "
        f"Module: {task.module or 'none'}. "
        f"Description: {task.description}. "
        "Context:\n"
        f"{context_block}\n\n"
        "Instruction: Produce ONLY the complete and final Python code. "
        "Start directly with the first line of code. "
        "No explanations. No markdown. No backticks. "
        "No comments except docstrings."
    )


# ============================================================
#  Correction Prompt (v3)
# ============================================================

def build_correction_prompt(
    task: Task,
    ctx: Dict[str, Any],
    spec_profile: Dict[str, Any],
    errors_summary: str
) -> str:
    """
    v3 correction prompt:
    - fix ONLY the listed issues
    - no structural changes unless required
    - code-only output
    """

    # Context assembly
    context_parts = []
    for f in ctx.get("files", []):
        path = f.get("path", "")
        content = f.get("content", "")
        context_parts.append(f"FILE {path}:\n{content}")

    context_block = "\n\n".join(context_parts) if context_parts else "No context."

    # Errors
    numbered = []
    for i, line in enumerate(errors_summary.strip().splitlines(), start=1):
        numbered.append(f"{i}. {line}")
    errors_block = "\n".join(numbered) if numbered else "No errors."

    return (
        f"Task: {task.name}. "
        f"Module: {task.module or 'none'}. "
        f"Description: {task.description}. "
        "Context:\n"
        f"{context_block}\n\n"
        "Errors:\n"
        f"{errors_block}\n\n"
        "Instruction: Fix ONLY the listed issues. "
        "Do not add new functions. "
        "Do not change structure except where required to fix errors. "
        "Return ONLY the corrected Python code. "
        "Start directly with the first line of code. "
        "No explanations. No markdown. No backticks. "
        "No comments except docstrings."
    )
