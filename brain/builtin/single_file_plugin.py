# Datei: brain/builtin/single_file_plugin.py

from __future__ import annotations
from typing import Dict, Any

from brain.base import BrainPlugin
from core.models import Task
from core.plugins.registry import PluginResult


class SingleFilePlugin(BrainPlugin):
    """
    Neutrales Standard-Plugin:
    - akzeptiert alle Task-Typen
    - erzeugt keine Subtasks (Single-File-Flow)
    """

    name = "single_file_plugin"
    task_types = ["*"]

    def matches(self, task: Task) -> bool:
        # universell: jedes Task-Objekt wird akzeptiert
        return True

    def execute(
        self,
        task: Task,
        specs: Dict[str, Any],
        context: Dict[str, Any],
    ) -> PluginResult:
        # Keine Subtasks → Orchestrator läuft im Single-File-Modus
        return PluginResult(subtasks=[])
