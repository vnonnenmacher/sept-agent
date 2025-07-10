import httpx
from typing import List
from .llm import BaseLlm


class LlamaLlm(BaseLlm):
    def __init__(self, model: str = "llama3", base_url: str = "http://ollama:11434"):
        self.model = model
        self.base_url = base_url

    def generate_response(self, query: str, chunks: List[str], context: dict) -> str:
        context_snippets = "\n\n".join(chunks)

        prompt = (
            "Você é um assistente clínico especializado em sepse, treinado com base no protocolo institucional. "
            "Sempre responda em português, com base apenas nas informações fornecidas.\n\n"
            f"🧠 Pergunta:\n{query}\n\n"
            f"📚 Trechos relevantes do protocolo:\n{context_snippets}\n\n"
        )

        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=240
        )

        response.raise_for_status()
        return response.json()["response"]

    def generate_from_prompt(self, prompt: str) -> str:

        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=480
        )

        response.raise_for_status()
        return response.json()["response"]
