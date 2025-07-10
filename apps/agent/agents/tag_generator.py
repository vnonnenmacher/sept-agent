import json
from typing import Any, Dict

from django.conf import settings

from apps.agent.agents.base_agent import BaseAgent
from apps.agent.models import Tag, TagCondition, DocumentChunk
from apps.agent.llms.openai_llm import OpenAiLlm
from apps.agent.llms.llama_llm import LlamaLlm
from apps.agent.utils import clean_json_output
from apps.protocols.chunking import split_into_chunks
from apps.protocols.models import KnowledgeDocument


class TagGenerationAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.llm = OpenAiLlm()  # Default to OpenAI LLM for now

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        document_text = input_data["document_text"]
        filename = input_data["filename"]
        version = input_data.get("version", "v1")

        chunks = split_into_chunks(document_text, size=500, overlap=50)
        document = KnowledgeDocument.objects.filter(minio_path=filename).first()
        all_tags = []

        self.log_event("Starting tag extraction", {"chunks": len(chunks)})

        for i, chunk_text in enumerate(chunks):
            chunk_obj, _ = DocumentChunk.objects.get_or_create(
                document=document,
                chunk_index=i,
                defaults={"text": chunk_text}
            )

            if chunk_obj.processed:
                continue

            prompt = self._build_prompt(chunk_text, chunk_number=i + 1)
            self.log_event("Sending prompt to LLM", {"chunk": i + 1})
            response = self.llm.generate_from_prompt(prompt)

            self.log_event("Received LLM response", {"chunk": i + 1, "preview": response[:200]})

            try:
                tags = clean_json_output(response)
                assert isinstance(tags, list)
                all_tags.append((tags, chunk_obj))
                chunk_obj.processed = True
                chunk_obj.last_error = None
            except Exception as e:
                self.log_event("Failed to parse chunk", {"chunk": i + 1, "error": str(e)})
                chunk_obj.last_error = str(e)

            chunk_obj.processing_attempts += 1
            chunk_obj.save()

        for tags, chunk in all_tags:
            self._store_tags_in_db(tags, document, chunk)

        return {"num_chunks_processed": len(all_tags)}

    def _build_prompt(self, chunk: str, chunk_number: int = None) -> str:
        chunk_info = f"(Parte {chunk_number})" if chunk_number else ""

        return f"""
#INSTRUÇÃO
Você é uma automação clínica responsável por extrair TAGS CLÍNICAS interpretáveis a partir de protocolos médicos.
NÃO ESCREVA COMENTÁRIOS OU QUALQUER OUTRO TEXTO FORA DO JSON. NÃO USE blocos como ```json.

Cada TAG representa uma condição clínica que pode ser associada a um paciente. A saída deve ser uma lista JSON de objetos com os campos:

- name: identificador curto
- display_name: nome legível
- description: descrição clínica
- category: ex: "sepse"
- conditions: lista de condições necessárias para a tag ser ativada.

Cada condição pode ter:
- type: "field", "tag", "event", ou "natural_language"
- name: nome da variável ou condição (obrigatório para todos os tipos exceto "natural_language")
- field_path (se type == "field")
- operator(se for comparação numérica)
- expression (se type == "natural_language")
- value ( somente valores numéricos, ex. 90, 38.5, etc.)

Exemplo:
[
  {{
    "name": "hipotensao",
    "display_name": "Hipotensão",
    "description": "Pressão sistólica menor que 90 mmHg",
    "category": "sepse",
    "conditions": [
      {{
        "type": "field",
        "name": "pressao_sistolica",
        "field_path": "vitals.pressao_sistolica",
        "operator": "<",
        "value": 90
      }}
    ]
  }}
]

📄 PROTOCOLO CLÍNICO {chunk_info}:
{chunk}
"""

    def _store_tags_in_db(self, tags: list[dict], document, chunk):
        for tag_data in tags:
            tag, _ = Tag.objects.get_or_create(
                name=tag_data.get("name"),
                defaults={
                    "display_name": tag_data.get("display_name", tag_data.get("name", "").capitalize()),
                    "description": tag_data.get("description", ""),
                    "category": tag_data.get("category", "default"),
                    "document": document,
                    "chunk": chunk,
                    "is_active": True,
                },
            )

            for cond in tag_data.get("conditions", []):
                if cond.get("type") == "natural_language" and cond.get("expression"):
                    TagCondition.objects.create(
                        tag=tag,
                        condition_type=cond["type"],
                        name="natural_expression",
                        expression=cond["expression"]
                    )
                elif "name" in cond:
                    TagCondition.objects.create(
                        tag=tag,
                        condition_type=cond["type"],
                        name=cond["name"],
                        field_path=cond.get("field_path"),
                        operator=cond.get("operator"),
                        value=cond.get("value"),
                        expression=cond.get("expression"),
                    )
