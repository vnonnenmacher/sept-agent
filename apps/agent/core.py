from .prompts import (
    build_antibiotic_prompt,
    build_next_step_prompt,
    build_ccih_prompt,
)
from .qdrant_search import retrieve_semantic_chunks
from django.conf import settings

if settings.LLM == "llama":
    from .llms.llama_llm import LlamaLlm
    llm = LlamaLlm()
elif settings.LLM == "openai":
    from .llms.openai_llm import OpenAiLlm
    llm = OpenAiLlm()


def define_antibiotic(patient_context: dict) -> str:
    query = build_antibiotic_prompt(patient_context)
    chunks = retrieve_semantic_chunks(query)
    return llm.generate_response(query, chunks, patient_context)


def define_next_step(patient_context: dict) -> str:
    query = build_next_step_prompt(patient_context)
    chunks = retrieve_semantic_chunks(query)
    return llm.generate_response(query, chunks, patient_context)


def suggest_ccih_recommendations(patient_context: dict) -> str:
    query = build_ccih_prompt(patient_context)
    chunks = retrieve_semantic_chunks(query)
    return llm.generate_response(query, chunks, patient_context)
