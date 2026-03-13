import requests
import json

class OllamaClient:
    """
    Stabiler Ollama-Client mit Streaming-Support.
    """

    def __init__(self, model="qwen2.5-coder:latest"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }

        try:
            response = requests.post(self.url, json=payload, stream=True, timeout=120)
            response.raise_for_status()

            full_text = ""

            for line in response.iter_lines():
                if not line:
                    continue

                try:
                    data = json.loads(line.decode("utf-8"))
                    chunk = data.get("response", "")
                    full_text += chunk
                except:
                    continue

            return full_text.strip()

        except Exception as e:
            return f"# LLM Error: {e}"
