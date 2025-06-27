import uuid
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    VectorParams,
    Distance
)

# Qdrant config
COLLECTION_NAME = "clinical_knowledge"
VECTOR_SIZE = 768

# Qdrant client
client = QdrantClient(host="qdrant", port=6333)

# Lazy-loaded BioBERT model
@lru_cache()
def get_model():
    print("📦 Loading BioBERT model (pritamdeka/BioBERT...)")
    return SentenceTransformer("pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb")

# Embedding and storage function
def embed_and_store_chunks(chunks, metadata_base):
    # Ensure the collection exists
    if not client.collection_exists(COLLECTION_NAME):
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        print(f"✅ Qdrant collection '{COLLECTION_NAME}' created.")
    else:
        print(f"✔️ Qdrant collection '{COLLECTION_NAME}' already exists.")

    # Get model
    model = get_model()

    # Generate points
    points = []
    for chunk in chunks:
        embedding = model.encode(chunk, normalize_embeddings=True)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={**metadata_base, "text": chunk}
        ))

    # Upsert to Qdrant
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"📤 Inserted {len(points)} vectors into '{COLLECTION_NAME}'")
