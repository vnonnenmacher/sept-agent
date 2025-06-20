from .client import qdrant, embedding_model
from qdrant_client.http import models


def search(query_text: str, filter_type: str = None, limit: int = 5):
    vector = embedding_model.encode(query_text).tolist()

    filters = None
    if filter_type:
        filters = models.Filter(
            must=[
                models.FieldCondition(
                    key="type",
                    match=models.MatchValue(value=filter_type)
                )
            ]
        )

    results = qdrant.search(
        collection_name="clinical-data",
        query_vector=vector,
        query_filter=filters,
        limit=limit
    )

    return results
