from __future__ import annotations

import hashlib
import json
import os
from typing import List

from core.models import SnapshotFile, SnapshotManifest


# ============================================================
#  Relevant Extensions (v3)
# ============================================================

RELEVANT_EXTENSIONS = {
    ".py", ".pyi",
    ".js", ".jsx",
    ".ts", ".tsx",
    ".json", ".yaml", ".yml",
}

IGNORED_DIRS = {
    ".git",
    "node_modules",
    ".runs",
    "runs",
    "dist",
    "build",
    "__pycache__",
}


# ============================================================
#  Hashing
# ============================================================

def _hash_file(path: str) -> str:
    """
    Deterministic SHA-256 hashing for snapshot files.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ============================================================
#  Snapshot Creation (v3)
# ============================================================

def create_snapshot(root: str) -> SnapshotManifest:
    """
    Creates a deterministic snapshot of the codebase.
    - filters by relevant extensions
    - ignores irrelevant directories
    - sorts files deterministically
    - never crashes (returns empty snapshot on failure)
    """

    files: List[SnapshotFile] = []

    try:
        for dirpath, dirnames, filenames in os.walk(root):
            # Remove ignored directories deterministically
            dirnames[:] = sorted(
                [d for d in dirnames if d not in IGNORED_DIRS]
            )

            for filename in sorted(filenames):
                ext = os.path.splitext(filename)[1]
                if ext not in RELEVANT_EXTENSIONS:
                    continue

                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root)

                try:
                    file_hash = _hash_file(full_path)
                except Exception:
                    file_hash = "ERROR"

                files.append(SnapshotFile(path=rel_path, hash=file_hash))

    except Exception:
        # Never crash — return empty snapshot
        return SnapshotManifest(files=[])

    # Deterministic ordering
    files = sorted(files, key=lambda f: f.path)

    return SnapshotManifest(files=files)


# ============================================================
#  Snapshot Saving (v3)
# ============================================================

def save_snapshot(manifest: SnapshotManifest, run_id: str) -> str:
    """
    Saves the snapshot in the v3 audit folder:
    runs/<run_id>/codebase_manifest.json
    """

    run_dir = os.path.join("runs", run_id)
    os.makedirs(run_dir, exist_ok=True)

    output_path = os.path.join(run_dir, "codebase_manifest.json")

    with open(output_path, "w", encoding="utf-8") as fp:
        json.dump(
    {
        "files": [
            {"path": f.path, "hash": f.hash}
            for f in manifest.files
        ]
    },
    fp,
    indent=2
)


    return output_path
