from openai import OpenAI
from typing import List
from .llm import BaseLlm


class OpenAiLlm(BaseLlm):
    def __init__(self, model: str = "gpt-4o"):
        self.client = OpenAI(
            api_key="your-api-key-here")  # Replace with your actual OpenAI API key
        self.model = model

    def generate_response(self, query: str, chunks: List[str], context: dict) -> str:
        context_snippets = "\n\n".join(chunks)

        messages = [
            {
                "role": "system",
                "content": (
                    "Você é um assistente clínico especializado em sepse, treinado com base no protocolo institucional. "
                    "Sempre responda em português, com base apenas nas informações fornecidas."
                )
            },
            {
                "role": "user",
                "content": (
                    f"🧠 Situação clínica:\n{query}\n\n"
                    f"📚 Trechos relevantes do protocolo:\n{context_snippets}\n\n"
                    "Com base nesses trechos e na situação atual, o que deve ser feito? Justifique sua resposta."
                )
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        return response.choices[0].message.content
