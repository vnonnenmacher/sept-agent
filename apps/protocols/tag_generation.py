import json
from apps.agent.llms.openai_llm import OpenAiLlm
from apps.agent.models import Tag, TagCondition
from .models import KnowledgeDocument
from apps.protocols.chunking import split_into_chunks
from apps.agent.llms.llama_llm import LlamaLlm

from django.conf import settings

if settings.LLM == "llama":
    llm = LlamaLlm()
elif settings.LLM == "openai":
    llm = OpenAiLlm()


def create_tags_from_document(document_text: str, filename: str, version: str = "v1"):
    """
    Chunk the document, call the LLM, and create Tag/TagCondition entries.
    """
    chunks = split_into_chunks(document_text, size=500, overlap=50)

    all_tags = []

    print(f'🔍 Processing document for tag extraction... {len(chunks)} chunks to be analized')

    for i, chunk in enumerate(chunks):
        prompt = _build_prompt(chunk, chunk_number=i + 1)

        print(f'🔍 Requesting llm to generate tags for chunk {i} of {len(chunks)} ...')
        response = llm.generate_from_prompt(prompt)

        print(f'Response from LLM for chunk {i + 1}: {response[:1000]}...')  # Log first 1000 chars

        try:
            tags = json.loads(response)
            assert isinstance(tags, list)
            all_tags.extend(tags)
        except Exception as e:
            print(f"⚠️ Failed to parse tags from chunk {i + 1}: {e}, stoping ...")
            raise e

        if i < 1:
            break  # For testing, process only the first chunk

    merged_tags = _deduplicate_tags(all_tags)
    document = KnowledgeDocument.objects.filter(minio_path=filename).first()

    _store_tags_in_db(merged_tags, document)


def _build_prompt(chunk: str, chunk_number: int = None) -> str:
    chunk_info = f"(Parte {chunk_number})" if chunk_number else ""

    return f"""
#INSTRUÇÃO
Você é uma automação clínica responsável por extrair TAGS CLÍNICAS interpretáveis a partir de protocolos médicos.  
NÃO ATUE COMO UM ASSISTENTE.  
NÃO ESCREVA COMENTÁRIOS, EXPLICAÇÕES OU FRASES.  
NÃO USE COLCHETES DUPLOS `[[`.  
A SAÍDA DEVE SER APENAS UM JSON VÁLIDO, PRONTO PARA INSERÇÃO EM BANCO DE DADOS.

---

📌 Uma **TAG clínica** representa uma **condição interpretável que pode ser atribuída a um paciente**, como por exemplo:
- "hipotensao"
- "temperatura_anormal"
- "sepse_suspeita"
- "disfunção_renal_aguda"

⚠️ NÃO extraia nomes de campos ou sinais vitais como tags. Ex: "temperatura", "PAS", "FC", "creatinina" são campos — use-os apenas dentro de `conditions`, nunca como `name` da tag.

---

✅ ESTRUTURA DO JSON ESPERADA (pronta para inserção no banco):

```json
[
  {{
    "name": "hipotensao",
    "display_name": "Hipotensão",
    "description": "Pressão arterial sistólica abaixo de 90 mmHg",
    "category": "sepse",
    "conditions": [
      {{
        "type": "field",
        "name": "pressao_sistolica",
        "field_path": "vitals.pressao.sistolica",
        "operator": "<",
        "value": 90,
        "status": null,
        "time_relation": null
      }}
    ]
  }}
]
```

📝 Detalhamento dos campos usados em `conditions`:
- `type`: "field", "tag" ou "event"
- `name`: nome do campo, tag ou evento
- `field_path`, `operator`, `value`: usados **somente** quando `type` = "field"
- `status`, `time_relation`: usados **somente** quando `type` = "event"

🔁 Use essa estrutura para cada condição extraída.

🛑 **NÃO INCLUA NENHUM TEXTO FORA DO JSON.**

---

📄 PROTOCOLO CLÍNICO {chunk_info}:
{chunk}
"""


def _deduplicate_tags(tag_list: list[dict]) -> list[dict]:
    seen = {}
    for tag in tag_list:
        key = tag["name"].strip().lower()
        if key not in seen:
            seen[key] = tag
        else:
            # Merge conditions
            existing = seen[key]
            existing_conditions = {json.dumps(c, sort_keys=True) for c in existing.get("conditions", [])}
            new_conditions = {json.dumps(c, sort_keys=True) for c in tag.get("conditions", [])}
            merged_conditions = list({*existing_conditions, *new_conditions})
            existing["conditions"] = [json.loads(c) for c in merged_conditions]
    return list(seen.values())


def _store_tags_in_db(tags: list[dict], document):
    for tag_data in tags:
        tag, created = Tag.objects.get_or_create(
            name=tag_data["name"],
            defaults={
                "display_name": tag_data.get("display_name", tag_data["name"].capitalize()),
                "description": tag_data.get("description", ""),
                "category": tag_data.get("category", "default"),
                "document": document,
                "is_active": True,
            }
        )
        for cond in tag_data.get("conditions", []):
            TagCondition.objects.create(
                tag=tag,
                condition_type=cond["type"],
                name=cond["name"],
                field_path=cond.get("field_path"),
                operator=cond.get("operator"),
                value=cond.get("value"),
                status=cond.get("status"),
                time_relation=cond.get("time_relation"),
            )
