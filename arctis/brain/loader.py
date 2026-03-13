# Datei: brain/loader.py

from __future__ import annotations
from typing import List, Type

from core.plugins.registry import PluginRegistry
from brain.base import BrainPlugin


def load_brain_plugins(plugins: List[Type[BrainPlugin]]) -> None:
    """
    Registriert alle Brain-Plugins im globalen PluginRegistry.
    """
    for plugin_cls in plugins:
        PluginRegistry.register(plugin_cls)
