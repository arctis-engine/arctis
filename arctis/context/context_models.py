from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RepoContext:
    files: List[str]
    functions: Dict[str, List[str]]
    classes: Dict[str, List[str]]
    imports: Dict[str, List[str]]
    layers: Dict[str, str]
    rules: Dict[str, List[str]] = field(default_factory=dict)

    # IR-Objekte pro Datei
    routes: Dict[str, list] = field(default_factory=dict)
    services: Dict[str, list] = field(default_factory=dict)
    models: Dict[str, list] = field(default_factory=dict)
