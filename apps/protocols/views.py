from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from .minio_utils import upload_to_minio
from .tasks import process_uploaded_protocol
from rest_framework.permissions import AllowAny
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue


class ProtocolUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "Arquivo não enviado."}, status=status.HTTP_400_BAD_REQUEST)

        version = request.data.get("version", "v1")

        try:
            upload_to_minio(bucket="protocols", filename=file.name, file_obj=file)
            process_uploaded_protocol.delay(file.name, version)
            return Response({"status": "Upload recebido, processamento iniciado."}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProtocolSemanticSearchView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        query = request.data.get("query")
        if not query:
            return Response({"error": "Campo 'query' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        model = SentenceTransformer("pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb")
        client = QdrantClient(host="qdrant", port=6333)

        vector = model.encode(query, normalize_embeddings=True)

        results = client.search(
            collection_name="clinical_knowledge",
            query_vector=vector,
            limit=5,
            with_payload=True
        )

        return Response({
            "results": [
                {
                    "score": r.score,
                    "text": r.payload.get("text"),
                    "source": r.payload.get("source"),
                    "version": r.payload.get("source_version"),
                } for r in results
            ]
        })
