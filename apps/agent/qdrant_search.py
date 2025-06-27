from functools import lru_cache
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

client = QdrantClient(host="qdrant", port=6333)

@lru_cache()
def get_embedding_model():
    print("📦 Loading BioBERT model (pritamdeka/BioBERT...)")
    return SentenceTransformer("pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb")


def retrieve_semantic_chunks(query: str, top_k: int = 5) -> list[str]:
    print(f"🔍 Performing semantic search for: {query}")
    model = get_embedding_model()
    vector = model.encode(query, normalize_embeddings=True)

    results = client.search(
        collection_name="clinical_knowledge",
        query_vector=vector,
        limit=top_k,
        with_payload=True
    )
    return [r.payload["text"] for r in results]
