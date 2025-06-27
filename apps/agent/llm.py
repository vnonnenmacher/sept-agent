from openai import OpenAI

openai_client = OpenAI(
    api_key="your-api-key-here",
)


def generate_response_from_llm(query: str, chunks: list[str], context: dict) -> str:
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

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    return response.choices[0].message.content
