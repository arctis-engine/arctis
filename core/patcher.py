from __future__ import annotations

import ast
import hashlib
import os
from typing import Optional

from core.models import Patch, PatchMode
from core.failures import FailureMode


# ============================================================
#  Hashing
# ============================================================

def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ============================================================
#  AST-basierte Funktions-Extraktion
# ============================================================

def _extract_first_function(code: str) -> Optional[ast.FunctionDef]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            return node
    return None


def _extract_first_class_method(code: str, class_name: str) -> Optional[ast.FunctionDef]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    return child
    return None


# ============================================================
#  AST-basierte Funktions-Ersetzung
# ============================================================

def _replace_function_in_file(old_source: str, new_func: ast.FunctionDef) -> str:
    """
    Replaces exactly one function in a Python file using AST.
    - preserves imports
    - preserves other functions
    - preserves classes
    - deterministic
    """

    try:
        old_tree = ast.parse(old_source)
    except SyntaxError:
        return old_source  # never destroy file

    new_name = new_func.name
    new_body = []
    replaced = False

    for node in old_tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == new_name:
            new_body.append(new_func)
            replaced = True
        else:
            new_body.append(node)

    if not replaced:
        new_body.append(new_func)

    old_tree.body = new_body
    return ast.unparse(old_tree)


def _replace_class_method_in_file(old_source: str, class_name: str, new_method: ast.FunctionDef) -> str:
    """
    Replaces a method inside a class.
    """

    try:
        old_tree = ast.parse(old_source)
    except SyntaxError:
        return old_source

    for node in old_tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            new_body = []
            replaced = False

            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == new_method.name:
                    new_body.append(new_method)
                    replaced = True
                else:
                    new_body.append(child)

            if not replaced:
                new_body.append(new_method)

            node.body = new_body

    return ast.unparse(old_tree)


# ============================================================
#  Patch-Erzeugung (v3)
# ============================================================

def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def create_patch(target_file: str, new_content: str, root: str, mode: PatchMode, function_name: Optional[str] = None) -> Patch:
    full_path = os.path.join(root, target_file)

    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            old_content = f.read()
        base_hash = _hash_content(old_content)
    else:
        old_content = ""
        base_hash = None

    return Patch(
        target_file=target_file,
        base_hash=base_hash,
        mode=mode,
        new_content=new_content,
        diff=None,
        function_name=function_name,
        language="python",
    )


# ============================================================
#  Patch-Anwendung (v3, sicher, deterministisch)
# ============================================================

def apply_patch(patch: Patch, root: str) -> Optional[FailureMode]:
    full_path = os.path.join(root, patch.target_file)

    # ------------------------------------------------------------
    # 1. Load current content
    # ------------------------------------------------------------
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            current_content = f.read()

        # Hash check
        if patch.base_hash is not None:
            if _hash_content(current_content) != patch.base_hash:
                return FailureMode.PATCH_HASH_MISMATCH
    else:
        current_content = ""

    # ------------------------------------------------------------
    # 2. Syntax check for new content
    # ------------------------------------------------------------
    try:
        ast.parse(patch.new_content)
    except SyntaxError:
        return FailureMode.PATCH_INVALID_CODE

    # ------------------------------------------------------------
    # 3. Apply patch based on mode
    # ------------------------------------------------------------
    final_content = current_content

    try:
        if patch.mode == PatchMode.FILE:
            final_content = patch.new_content

        elif patch.mode == PatchMode.FUNCTION:
            func = _extract_first_function(patch.new_content)
            if func is None:
                return FailureMode.PATCH_INVALID_CODE
            final_content = _replace_function_in_file(current_content, func)

        elif patch.mode == PatchMode.CLASS_METHOD:
            if not patch.function_name:
                return FailureMode.PATCH_INVALID_CODE

            method = _extract_first_function(patch.new_content)
            if method is None:
                return FailureMode.PATCH_INVALID_CODE

            final_content = _replace_class_method_in_file(
                current_content,
                class_name=patch.function_name.split(".")[0],
                new_method=method,
            )

        elif patch.mode == PatchMode.INSERT:
            final_content = current_content + "\n" + patch.new_content

        elif patch.mode == PatchMode.DELETE:
            # naive delete: remove exact match
            final_content = current_content.replace(patch.new_content, "")

        else:
            return FailureMode.PATCH_INVALID_CODE

    except Exception:
        return FailureMode.PATCH_APPLY_FAILED

    # ------------------------------------------------------------
    # 4. Ensure directory exists
    # ------------------------------------------------------------
    directory = os.path.dirname(full_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    # ------------------------------------------------------------
    # 5. Write final content
    # ------------------------------------------------------------
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(final_content)

    return None  # success
