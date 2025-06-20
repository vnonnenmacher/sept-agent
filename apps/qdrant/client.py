from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


qdrant = QdrantClient("qdrant", port=6333)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
