# sync_documents.py
from .models import KnowledgeDocument
from .minio_utils import list_documents_in_minio


def sync_documents_from_minio():
    existing_paths = set(KnowledgeDocument.objects.values_list("minio_path", flat=True))
    current_files = list_documents_in_minio()

    new_files = []
    for obj in current_files:
        if obj["path"] not in existing_paths:
            parts = obj["path"].split("/")
            filename = parts[-1]
            category, version, *_ = filename.split("__")  # e.g. protocolo__v1__abc.pdf
            new_files.append(KnowledgeDocument(
                name=filename,
                category=category,
                version=version,
                minio_path=obj["path"]
            ))

    KnowledgeDocument.objects.bulk_create(new_files)
