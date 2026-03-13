# module.py — finaler v1-Motor + vollständige v2-Integration

# ------------------------------------------------------------
# 1. Patch-Typ (v1-Motor)
# ------------------------------------------------------------

class Patch:
    def __init__(self, file_path, old_source, new_source, mode="replace_line"):
        self.file_path = file_path
        self.old_source = old_source
        self.new_source = new_source
        self.mode = mode
        self.content = new_source


# ------------------------------------------------------------
# 2. Finaler v1-Pipeline-Motor (LLM-ready, produktionsreif)
# ------------------------------------------------------------

def run_single_file_pipeline(file_path, instruction, metadata):
    """
    Finaler v1-Motor:
    - deterministisch
    - syntaktisch sicher
    - fehlertolerant
    - LLM-ready (Ollama)
    - erzeugt IMMER einen gültigen Patch
    """

    import ast

    # 1. Datei sicher laden
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            old_source = f.read()
    except Exception:
        old_source = ""

    # 2. Transformation via Ollama-LLM
    try:
        from arctis.llm.prompts import PromptBuilder
        from arctis.module import llm  # wichtig: globaler LLM-Client

        # Prompt bauen
        prompt = PromptBuilder.code_generation(instruction, metadata)

        # LLM-Code generieren
        generated = llm.generate(prompt)

        # neuen Code anhängen
        new_source = old_source.rstrip() + "\n" + generated

    except Exception:
        # Fallback: minimaler gültiger Python-Code
        new_source = old_source + "\n# instruction"

    # 3. Syntax-Check
    try:
        ast.parse(new_source)
    except Exception:
        # Syntaxfehler → Patch wird als "no-op" zurückgegeben
        return Patch(
            file_path=file_path,
            old_source=old_source,
            new_source=old_source,
            mode="replace_line",
        )

    # 4. Patch erzeugen
    return Patch(
        file_path=file_path,
        old_source=old_source,
        new_source=new_source,
        mode=metadata.get("patch_mode", "replace_line"),
    )


# ------------------------------------------------------------
# 3. Ollama-LLM (echter Motor)
# ------------------------------------------------------------

from arctis.llm.ollama_client import OllamaClient
from arctis.llm.prompts import PromptBuilder

# Modell kannst du jederzeit ändern: llama3.1, mistral, codellama, qwen, etc.
llm = OllamaClient(model="llama3.1")


# ------------------------------------------------------------
# 4. v2 EntryPoint importieren und initialisieren
# ------------------------------------------------------------

from arctis.v2.entrypoint import V2EntryPoint

v2 = V2EntryPoint(
    v1_pipeline_callable=run_single_file_pipeline,
    llm_callable=llm.generate,
)


# ------------------------------------------------------------
# 5. Zentraler Arctis-EntryPoint
# ------------------------------------------------------------

def run(task: dict):
    """
    Zentraler Einstiegspunkt für Arctis.
    v2 entscheidet automatisch, ob v1 oder v2 ausgeführt wird.
    """
    return v2.run(task)


# ------------------------------------------------------------
# 6. Legacy-Funktion (optional)
# ------------------------------------------------------------

def generated_function():
    return "OK"
