from typing import Optional, Any


class Enforcement:
    """
    Finale Entscheidungsschicht.
    Kombiniert:
    - Spec-Engine
    - Struktur-Validator
    - Sanitizer
    """

    def enforce(
        self,
        patch: Any,
        spec_ok: bool,
        structure_ok: bool,
        sanitized_patch: Optional[Any],
    ) -> Optional[Any]:
        """
        Gibt den final erlaubten Patch zurück oder None.
        """

        if not spec_ok:
            return None

        if not structure_ok:
            return None

        if sanitized_patch is None:
            return None

        return sanitized_patch
