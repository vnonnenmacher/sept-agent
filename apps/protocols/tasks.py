from celery import shared_task
from .minio_utils import download_from_minio
from .pdf_extraction import extract_text_from_pdf
from .chunking import split_into_chunks
from apps.qdrant.qdrant_utils import (
    embed_and_store_chunks,
    COLLECTION_NAME,
    client as qdrant_client,
)
from qdrant_client.models import VectorParams, Distance


@shared_task
def process_uploaded_protocol(filename: str, version: str = "v1"):
    # ✅ Criação segura da coleção se ela não existir
    if not qdrant_client.collection_exists(COLLECTION_NAME):
        qdrant_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=768,
                distance=Distance.COSINE
            )
        )

    # 🧾 Baixa o PDF e processa
    pdf_path = download_from_minio(bucket="protocols", filename=filename)
    full_text = extract_text_from_pdf(pdf_path)
    chunks = split_into_chunks(full_text)

    # 📤 Envia embeddings ao Qdrant
    embed_and_store_chunks(
        chunks,
        metadata_base={"source": filename, "source_version": version}
    )
