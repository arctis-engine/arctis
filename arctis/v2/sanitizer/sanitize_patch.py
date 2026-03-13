from typing import Any


class PatchSanitizer:
    """
    Säubert Patch-Objekte, bevor sie geschrieben werden.
    Erwartet ein Patch-Objekt aus v1.
    """

    MAX_PATCH_SIZE = 5000  # Sicherheitsgrenze

    def sanitize(self, patch: Any) -> Any:
        if patch is None:
            return None

        # Full-Rewrite verhindern
        if getattr(patch, "mode", None) == "rewrite":
            return None

        # Patch darf nicht zu groß sein
        if hasattr(patch, "content") and len(str(patch.content)) > self.MAX_PATCH_SIZE:
            return None

        # Entferne gefährliche Inhalte
        if hasattr(patch, "content"):
            forbidden = ["eval(", "exec(", "import os", "import subprocess"]
            for f in forbidden:
                if f in patch.content:
                    return None

        return patch
