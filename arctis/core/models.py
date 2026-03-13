from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any

from core.failures import FailureMode


# ============================================================
#  Versionierung
# ============================================================

MODEL_VERSION = 3


# ============================================================
#  Snapshot-Strukturen (für Audit & Reproduzierbarkeit)
# ============================================================

@dataclass
class SnapshotFile:
    """
    Einzelne Datei im Snapshot.
    """
    path: str
    hash: str


@dataclass
class SnapshotManifest:
    """
    Manifest aller Dateien eines Snapshots.
    """
    files: List[SnapshotFile] = field(default_factory=list)


# ============================================================
#  Issue / ValidationResult v3
# ============================================================

class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


@dataclass
class Issue:
    """
    Ein einzelnes Validierungsproblem.
    """
    code: str
    message: str
    severity: Severity = Severity.ERROR
    location: Optional[Dict[str, Any]] = None  # z.B. {"file": "...", "line": 12}


@dataclass
class ValidationResult:
    """
    Ergebnis der Validator-Pipeline.
    """
    ok: bool
    issues: List[Issue] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


# ============================================================
#  Patch v3
# ============================================================

class PatchMode(str, Enum):
    FUNCTION = "function"
    FILE = "file"
    CLASS_METHOD = "class_method"
    INSERT = "insert"
    DELETE = "delete"


@dataclass
class Patch:
    """
    Repräsentiert eine geplante Codeänderung.
    """
    target_file: str
    base_hash: Optional[str]
    mode: PatchMode
    new_content: str
    diff: Optional[str] = None
    function_name: Optional[str] = None
    language: str = "python"


# ============================================================
#  RunRecord v3
# ============================================================

class RunStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class RunRecord:
    """
    Vollständige Dokumentation eines einzelnen Runs.
    """
    run_id: str
    task_id: str
    input_hash: str
    seed: int
    snapshot_path: str

    status: RunStatus = RunStatus.PENDING
    failure_mode: Optional[FailureMode] = None

    # Liste von Dateien, die geändert wurden oder relevant waren
    files: List[Dict[str, Any]] = field(default_factory=list)

    # Meta-Informationen (Versionen, Task-Typ, Spec-Profil, etc.)
    meta: Dict[str, Any] = field(default_factory=dict)


# ============================================================
#  Task / Subtask v3
# ============================================================

@dataclass
class Task:
    """
    v3-Task-Definition (validiert durch TaskSchema).
    """
    id: str
    name: str
    type: str
    description: str

    module: Optional[str] = None
    target_file: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Subtask:
    """
    v3-Subtask (von Plugins erzeugt).
    """
    parent_task_id: str
    name: str
    type: str
    target_file: str
    meta: Dict[str, Any] = field(default_factory=dict)
