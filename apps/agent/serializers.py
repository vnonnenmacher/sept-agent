from rest_framework import serializers
from .models import Tag, TagCondition, DocumentChunk


class TagConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagCondition
        fields = [
            "id",
            "condition_type",
            "name",
            "field_path",
            "operator",
            "value",
            "expression",
        ]


class TagSerializer(serializers.ModelSerializer):
    conditions = TagConditionSerializer(many=True, read_only=True)
    document_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    chunk_index = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
            "display_name",
            "description",
            "category",
            "document",
            "document_name",
            "chunk",
            "chunk_index",
            "created_by",
            "created_by_name",
            "is_active",
            "created_at",
            "conditions",
        ]

    def get_document_name(self, obj):
        return getattr(obj.document, "title", None)

    def get_created_by_name(self, obj):
        return getattr(obj.created_by, "username", None)

    def get_chunk_index(self, obj):
        return getattr(obj.chunk, "chunk_index", None)


class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = [
            "id",
            "document",
            "chunk_index",
            "text",
            "processed",
            "processing_attempts",
            "last_error",
            "created_at",
            "updated_at",
        ]
