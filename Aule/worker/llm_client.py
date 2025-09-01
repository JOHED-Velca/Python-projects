import os
import httpx


class LLMClient:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "mock").lower()
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")


    def complete(self, prompt: str) -> str:
        if self.provider == "openai" and self.openai_key:
            return self._openai_complete(prompt)
        if self.provider == "ollama":
            return self._ollama_complete(prompt)
        return self._mock_complete(prompt)


    def _mock_complete(self, prompt: str) -> str:
        return (
            "Dear Hiring Manager,\n\n"
            "I’m excited to apply for this role. Based on my background, I align with the key requirements, "
            "and I’m confident I can contribute from day one.\n\n"
            "Sincerely,\nYour Name"
        )


    def _openai_complete(self, prompt: str) -> str:
        # Minimal, replace with openai client of your choice later
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json",
        }
        json = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
        }
        url = "https://api.openai.com/v1/chat/completions"
        with httpx.Client(timeout=60) as client:
            resp = client.post(url, headers=headers, json=json)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()


    def _ollama_complete(self, prompt: str) -> str:
        # Requires `ollama serve` and a pulled model (e.g., mistral)
        with httpx.Client(timeout=60) as client:
            resp = client.post(
            f"{self.ollama_host}/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "").strip()