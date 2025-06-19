from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import uuid


# 🚀 Setup dos clientes
client = QdrantClient("qdrant", port=6333)  # Nome do serviço no docker-compose
model = SentenceTransformer('all-MiniLM-L6-v2')


# 🚀 Função para garantir collection
def create_collection_if_not_exists():
    if not client.collection_exists(collection_name="clinical-data"):
        client.recreate_collection(
            collection_name="clinical-data",
            vectors_config=models.VectorParams(
                size=384,
                distance=models.Distance.COSINE
            )
        )
        print("✅ Collection 'clinical-data' created in Qdrant.")
    else:
        print("✔️ Collection 'clinical-data' already exists.")


# 🚀 Função para gerar texto
def generate_patient_text(patient):
    return (
        f"Patient {patient.name}, born on {patient.birth_date}, gender {patient.gender}."
    )


# 🚀 Função para vetorizar e salvar
def embed_and_store_patient(patient):
    create_collection_if_not_exists()  # 🔥 Garante que a collection existe

    text = generate_patient_text(patient)
    embedding = model.encode(text).tolist()

    point = models.PointStruct(
        id=str(uuid.uuid4()),
        vector=embedding,
        payload={
            "text": text,
            "type": "patient",
            "patient_id": patient.patient_id,
            "name": patient.name,
            "gender": patient.gender,
            "birth_date": str(patient.birth_date)
        }
    )

    client.upsert(
        collection_name="clinical-data",
        points=[point]
    )

    print(f"✅ Vetorizado e armazenado: {text}")
