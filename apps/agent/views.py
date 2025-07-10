from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, filters, mixins

from .core import (
    define_antibiotic,
    define_next_step,
    suggest_ccih_recommendations,
)
from .models import Tag, DocumentChunk, TagCondition
from .serializers import TagSerializer, DocumentChunkSerializer, TagConditionSerializer


class SuggestAntibioticView(APIView):
    def post(self, request):
        patient_context = request.data
        try:
            result = define_antibiotic(patient_context)
            return Response({"result": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SuggestNextStepView(APIView):
    def post(self, request):
        patient_context = request.data
        try:
            result = define_next_step(patient_context)
            return Response({"result": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SuggestCCIHSuggestionsView(APIView):
    def post(self, request):
        patient_context = request.data
        try:
            result = suggest_ccih_recommendations(patient_context)
            return Response({"result": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.filter(is_active=True)
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "display_name", "description", "category"]
    ordering_fields = ["created_at", "name"]
    ordering = ["name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        document_id = self.request.query_params.get("document_id")

        if category:
            queryset = queryset.filter(category=category)
        if document_id:
            queryset = queryset.filter(document_id=document_id)

        return queryset


class DocumentChunkViewSet(mixins.ListModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    queryset = DocumentChunk.objects.all().select_related("document")
    serializer_class = DocumentChunkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        document_id = self.request.query_params.get("document_id")
        if document_id:
            queryset = queryset.filter(document_id=document_id)
        return queryset


class TagConditionUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            condition = TagCondition.objects.get(pk=pk)
        except TagCondition.DoesNotExist:
            return Response({"detail": "Condition not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TagConditionSerializer(condition, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
