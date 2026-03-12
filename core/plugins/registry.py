# Datei: core/plugins/registry.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Type

from core.models import Task, Subtask
from core.failures import FailureMode


# ============================================================
#  Plugin-Result v3
# ============================================================

@dataclass
class PluginResult:
    subtasks: List[Subtask] = field(default_factory=list)
    failure: Optional[FailureMode] = None


# ============================================================
#  Plugin-Basis v3
# ============================================================

class Plugin:
    """
    Basisklasse für alle v3-Plugins.
    """

    name: str = "base_plugin"
    task_types: List[str] = []  # z.B. ["codegen.file", "patch.refactor"]

    def matches(self, task: Task) -> bool:
        return task.type in self.task_types

    def execute(self, task: Task, specs: Dict[str, Any], context: Dict[str, Any]) -> PluginResult:
        """
        Muss von Subklassen überschrieben werden.
        """
        raise NotImplementedError("Plugin.execute() must be implemented by subclasses.")

    def safe_execute(self, task: Task, specs: Dict[str, Any], context: Dict[str, Any]) -> PluginResult:
        """
        Fängt Plugin-Fehler ab und liefert FailureMode.PLUGIN_RUNTIME_ERROR.
        """
        try:
            return self.execute(task, specs, context)
        except Exception:
            return PluginResult(
                subtasks=[],
                failure=FailureMode.PLUGIN_RUNTIME_ERROR,
            )


# ============================================================
#  Plugin-Registry v3
# ============================================================

class PluginRegistry:
    """
    Globale Plugin-Registry.
    """
    _plugins: List[Plugin] = []

    @classmethod
    def register(cls, plugin_cls: Type[Plugin]):
        cls._plugins.append(plugin_cls())
        return plugin_cls

    @classmethod
    def find_for_task(cls, task: Task) -> List[Plugin]:
        return [p for p in cls._plugins if p.matches(task)]


# ============================================================
#  Convenience-Funktion
# ============================================================

def find_plugins_for_task(task: Task) -> List[Plugin]:
    return PluginRegistry.find_for_task(task)
