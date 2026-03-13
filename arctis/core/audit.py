from __future__ import annotations

import hashlib
import json
import os
import yaml
from typing import Any, Dict

from core.models import Patch, RunRecord, SnapshotManifest, Task, Subtask


RUNS_DIR = "runs"


# ============================================================
#  Helpers
# ============================================================

def _to_serializable(obj: Any) -> Any:
    """
    Converts Task, Subtask, Patch, RunRecord, SnapshotManifest
    into JSON/YAML‑serializable structures.
    """
    if obj is None:
        return None

    if isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, dict):
        return {k: _to_serializable(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [_to_serializable(x) for x in obj]

    # v3 models
    if hasattr(obj, "to_dict"):
        return obj.to_dict()

    if hasattr(obj, "__dict__"):
        return {
            k: _to_serializable(v)
            for k, v in obj.__dict__.items()
            if not k.startswith("_")
        }

    return str(obj)


# ============================================================
#  Input Hash (v3)
# ============================================================

def compute_input_hash(task: Task, spec_profile: Dict[str, Any], manifest: SnapshotManifest) -> str:
    data = {
        "task": _to_serializable(task),
        "spec_profile": spec_profile,
        "files": [
            {"path": f.path, "hash": f.hash}
            for f in manifest.files
        ],
    }
    serialized = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


# ============================================================
#  Run Folder
# ============================================================

def create_run_folder(run_id: str) -> str:
    path = os.path.join(RUNS_DIR, run_id)
    os.makedirs(path, exist_ok=True)
    return path


# ============================================================
#  Save Task / Subtask
# ============================================================

def save_task(task: Task | Subtask | Dict[str, Any], run_id: str, index: int = 0) -> None:
    """
    Saves the task or subtask as YAML.
    """
    path = os.path.join(RUNS_DIR, run_id, f"task_{index}.yaml")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(_to_serializable(task), f, allow_unicode=True)


# ============================================================
#  Save Context
# ============================================================

def save_context(ctx: Dict[str, Any], run_id: str, index: int = 0) -> None:
    path = os.path.join(RUNS_DIR, run_id, f"context_{index}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ctx, f, indent=2)


# ============================================================
#  Save Prompt / Response (versioned)
# ============================================================

def save_prompt(prompt: str, run_id: str, iteration: int = 0) -> None:
    path = os.path.join(RUNS_DIR, run_id, f"prompt_{iteration}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(prompt)


def save_response(response: str, run_id: str, iteration: int = 0) -> None:
    path = os.path.join(RUNS_DIR, run_id, f"response_{iteration}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(response)


# ============================================================
#  Save Patch (v3)
# ============================================================

def save_patch_file(patch, run_id, suffix=""):
    """
    Speichert den Patch als Datei im Run-Ordner.
    """
    run_dir = os.path.join("runs", run_id)
    os.makedirs(run_dir, exist_ok=True)

    filename = f"patch_{suffix}.txt" if suffix else "patch.txt"
    path = os.path.join(run_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(patch.new_content)

    return path


# ============================================================
#  Save Snapshot
# ============================================================

def save_snapshot(manifest: SnapshotManifest, run_id: str) -> None:
    path = os.path.join(RUNS_DIR, run_id, "snapshot.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_to_serializable(manifest), f, indent=2)


# ============================================================
#  Save Audit (v3)
# ============================================================

def save_audit(record: RunRecord, run_id: str) -> None:
    """
    Saves the final RunRecord as JSON.
    """
    path = os.path.join(RUNS_DIR, run_id, "audit.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(_to_serializable(record), f, indent=2)
