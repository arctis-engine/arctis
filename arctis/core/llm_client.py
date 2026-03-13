from __future__ import annotations

import hashlib
import json
import time
import urllib.request
import os
from typing import Optional, Dict, Any

from core.failures import FailureMode
from core.models import ValidationResult


# ============================================================
#  v3 Normalizer (deterministic, safe)
# ============================================================

def normalize_llm_output(text: str) -> str:
    """
    Arctic Brain v3:
    - entfernt Backticks
    - entfernt Markdown-Codeblöcke
    - entfernt Leading/Trailing Noise
    - deterministisch
    """
    if not text:
        return ""

    cleaned = text.replace("```", "").strip()

    # Entferne häufige LLM-Artefakte
    for prefix in ["Here is the code:", "Sure, here is", "Certainly"]:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()

    return cleaned


# ============================================================
#  Prompt Template (v3)
# ============================================================

_PROMPT_TEMPLATE = (
    "<system>\n{system_prompt}\n</system>\n\n"
    "<user>\n{user_prompt}\n</user>"
)


# ============================================================
#  Audit Logging (v3)
# ============================================================

def _write_llm_audit(audit: dict) -> None:
    log_dir = os.path.join("runs", "_llm_audit")
    os.makedirs(log_dir, exist_ok=True)
    timestamp = str(int(time.time() * 1000))
    path = os.path.join(log_dir, f"{timestamp}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)


# ============================================================
#  Base Interface
# ============================================================

class LLMClient:
    def generate(self, system_prompt: str, user_prompt: str, seed: int) -> tuple[str, Optional[FailureMode]]:
        raise NotImplementedError


# ============================================================
#  Dummy Client (für Tests)
# ============================================================

class DummyClient(LLMClient):
    def generate(self, system_prompt, user_prompt, seed):
        h = hashlib.sha256(f"{system_prompt}{user_prompt}{seed}".encode("utf-8")).hexdigest()
        return f"def dummy():\n    return '{h[:16]}'", None


# ============================================================
#  Ollama Client (v3)
# ============================================================

class OllamaClient(LLMClient):
    def __init__(
        self,
        model: Optional[str] = None,
        base_url: str = "http://localhost:11434",
        timeout: int = 650,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        json_mode: bool = False
    ):
        env_model = os.getenv("ARCTIC_MODEL")

        if env_model:
            self.model = env_model
        elif model:
            self.model = model
        else:
            raise RuntimeError("No model specified. Set ARCTIC_MODEL to a valid Ollama model name.")

        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.json_mode = json_mode

    # ----------------------------

    def _build_payload(self, prompt: str, seed: int) -> bytes:
        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "seed": seed,
                "temperature": 0
            }
        }
        if self.json_mode:
            body["format"] = "json"
        return json.dumps(body).encode("utf-8")

    # ----------------------------

    def _request(self, payload: bytes) -> dict:
        req = urllib.request.Request(
            url=f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    # ----------------------------

    def generate(self, system_prompt: str, user_prompt: str, seed: int) -> tuple[str, Optional[FailureMode]]:
        full_prompt = _PROMPT_TEMPLATE.format(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        payload = self._build_payload(full_prompt, seed)

        audit = {
            "model": self.model,
            "seed": seed,
            "json_mode": self.json_mode,
            "prompt_length": len(full_prompt),
            "prompt_hash": hashlib.sha256(full_prompt.encode("utf-8")).hexdigest(),
            "attempts": []
        }

        last_error = None

        for attempt in range(self.max_retries):
            attempt_record = {"attempt": attempt + 1}
            t_start = time.monotonic()

            try:
                result = self._request(payload)
                latency = round(time.monotonic() - t_start, 3)
                attempt_record["latency_s"] = latency

                if "error" in result:
                    raise RuntimeError(result["error"])

                content = result.get("response", "").strip()
                if not content:
                    raise RuntimeError("Empty response")

                content = normalize_llm_output(content)

                attempt_record["status"] = "success"
                attempt_record["response_length"] = len(content)
                audit["attempts"].append(attempt_record)
                audit["result"] = "success"

                _write_llm_audit(audit)
                return content, None

            except Exception as e:
                latency = round(time.monotonic() - t_start, 3)
                attempt_record["latency_s"] = latency
                attempt_record["status"] = "failed"
                attempt_record["error"] = str(e)
                audit["attempts"].append(attempt_record)
                last_error = e

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        audit["result"] = "failed"
        _write_llm_audit(audit)
        return "", FailureMode.LLM_UNAVAILABLE


# ============================================================
#  Multi-Model Router (v3)
# ============================================================

class MultiModelClient(LLMClient):
    def __init__(self, clients: Dict[str, LLMClient]):
        self.clients = clients

    def get(self, role: str) -> LLMClient:
        if role not in self.clients:
            raise ValueError(f"No client registered for role '{role}'")
        return self.clients[role]

    def generate(self, system_prompt: str, user_prompt: str, seed: int, role: str = "patch") -> tuple[str, Optional[FailureMode]]:
        return self.get(role).generate(system_prompt, user_prompt, seed)


# ============================================================
#  Factory Functions (v3)
# ============================================================

def get_llm_client(model: Optional[str] = None, json_mode: bool = False) -> LLMClient:
    if os.getenv("ARCTIC_TEST_MODE") == "1":
        return DummyClient()
    return OllamaClient(model=model, json_mode=json_mode)


def get_multi_model_client(
    analysis_model: Optional[str] = None,
    patch_model: Optional[str] = None,
    review_model: Optional[str] = None
) -> MultiModelClient:

    if os.getenv("ARCTIC_TEST_MODE") == "1":
        return MultiModelClient(clients={
            "analysis": DummyClient(),
            "patch": DummyClient(),
            "review": DummyClient()
        })

    return MultiModelClient(clients={
        "analysis": OllamaClient(model=analysis_model),
        "patch": OllamaClient(model=patch_model),
        "review": OllamaClient(model=review_model)
    })
