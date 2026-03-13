from __future__ import annotations

import os
import yaml
from typing import Dict, Any

from core.models import Task


# ============================================================
#  YAML Loader (deterministic, safe)
# ============================================================

def _load_yaml(path: str) -> dict:
    """
    Deterministic YAML loader:
    - returns {} on missing file
    - returns {} on invalid YAML
    - ensures dict output
    """
    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


# ============================================================
#  Deep Merge (v3)
# ============================================================

def _deep_merge(a: dict, b: dict) -> dict:
    """
    Deep merge for nested spec structures.
    project > global
    """
    result = dict(a)

    for key, value in b.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value

    return result


# ============================================================
#  Spec Loader (global + project)
# ============================================================

SPEC_FILES = [
    "rules.yaml",
    "modules.yaml",
    "patterns.yaml",
    "naming.yaml",
    "allowed_operations.yaml",
    "style.yaml",
    "structure.yaml",
    "forbidden.yaml",
]


def load_specs(root: str) -> dict:
    """
    Loads global + project specs in v3 format.
    """

    def load_group(base_path: str) -> dict:
        return {
            name.replace(".yaml", ""): _load_yaml(os.path.join(base_path, name))
            for name in SPEC_FILES
        }

    global_specs = load_group("specs")
    project_specs = load_group(os.path.join(root, "specs"))

    return {
        "global": global_specs,
        "project": project_specs,
    }


# ============================================================
#  Pattern Matching (deterministic)
# ============================================================

def _match_patterns(patterns: dict, task_name: str, task_path: str) -> dict:
    """
    v3 pattern matching:
    - exact match
    - prefix*
    - substring
    - deterministic
    """

    matched = {}

    for pattern, rules in patterns.items():
        if not isinstance(rules, dict):
            continue

        # Wildcard prefix*
        if "*" in pattern:
            prefix = pattern.replace("*", "")
            if task_name.startswith(prefix) or task_path.startswith(prefix):
                matched = _deep_merge(matched, rules)
                continue

        # Exact
        if pattern == task_name or pattern == task_path:
            matched = _deep_merge(matched, rules)
            continue

        # Substring
        if pattern in task_name or pattern in task_path:
            matched = _deep_merge(matched, rules)

    return matched


# ============================================================
#  Rule Aggregation (v3)
# ============================================================

def get_rules_for_task(specs: dict, task: Task) -> dict:
    """
    v3 rule aggregation:
    - global rules
    - module rules
    - pattern rules
    - naming
    - allowed operations
    - style
    - structure
    - forbidden
    """

    task_module = task.module
    task_name = task.name
    task_path = task.target_file or ""

    # Extract groups
    global_specs = specs["global"]
    project_specs = specs["project"]

    # Deep merge global + project
    merged = {
        key: _deep_merge(global_specs.get(key, {}), project_specs.get(key, {}))
        for key in global_specs.keys()
    }

    rules = merged.get("rules", {})
    modules = merged.get("modules", {})
    patterns = merged.get("patterns", {})
    naming = merged.get("naming", {})
    allowed_ops = merged.get("allowed_operations", {})
    style = merged.get("style", {})
    structure = merged.get("structure", {})
    forbidden = merged.get("forbidden", {})

    # Module rules
    module_rules = modules.get(task_module, {}) if task_module else {}

    # Pattern rules
    pattern_rules = _match_patterns(patterns, task_name, task_path)

    # Effective rules (v3 priority)
    effective = {}
    for group in [
        rules,
        module_rules,
        pattern_rules,
        naming,
        allowed_ops,
        style,
        structure,
        forbidden,
    ]:
        effective = _deep_merge(effective, group)

    return {
        "rules": rules,
        "module_rules": module_rules,
        "pattern_rules": pattern_rules,
        "naming": naming,
        "allowed_operations": allowed_ops,
        "style": style,
        "structure": structure,
        "forbidden": forbidden,
        "effective": effective,
    }
