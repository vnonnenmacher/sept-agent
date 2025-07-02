from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404

from apps.qdrant.qdrant_utils import delete_vectors_for_document

from .models import KnowledgeDocument
from .serializers import KnowledgeDocumentSerializer
from .minio_utils import (
    upload_to_minio,
    delete_from_minio,
    generate_presigned_url,
)
from rest_framework.permissions import AllowAny
from .tasks import process_uploaded_protocol
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue


class ProtocolUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get("file")
        category = request.data.get("category")
        version = request.data.get("version", "v1")

        if not file or not category:
            return Response(
                {"error": "File and category are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        filename = f"{category}__{version}__{file.name}"
        try:
            upload_to_minio("protocols", filename, file)

            KnowledgeDocument.objects.create(
                name=file.name,
                category=category,
                version=version,
                minio_path=filename,
            )

            process_uploaded_protocol.delay(filename, version)
            return Response(
                {"status": "Upload received, processing started."},
                status=status.HTTP_202_ACCEPTED
            )

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


class KnowledgeDocumentListView(ListAPIView):
    serializer_class = KnowledgeDocumentSerializer

    def get_queryset(self):
        queryset = KnowledgeDocument.objects.all()
        category = self.request.query_params.get("category")
        version = self.request.query_params.get("version")
        if category:
            queryset = queryset.filter(category=category)
        if version:
            queryset = queryset.filter(version=version)
        return queryset.order_by("-uploaded_at")


class KnowledgeDocumentDeleteView(APIView):
    def delete(self, request, pk):
        doc = get_object_or_404(KnowledgeDocument, pk=pk)
        try:
            delete_from_minio("protocols", doc.minio_path)
            delete_vectors_for_document(doc.minio_path)  # ✅ Remove from Qdrant
            doc.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KnowledgeDocumentDownloadView(APIView):
    def get(self, request, pk):
        doc = get_object_or_404(KnowledgeDocument, pk=pk)
        try:
            url = generate_presigned_url(doc.minio_path)
            return Response({"url": url})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
