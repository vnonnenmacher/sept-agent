from rest_framework import serializers
from .models import KnowledgeDocument


class KnowledgeDocumentSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgeDocument
        fields = [
            "id",
            "name",
            "category",
            "version",
            "minio_path",
            "uploaded_at",
            "download_url",
        ]
        read_only_fields = fields

    def get_download_url(self, obj):
        try:
            from .minio_utils import generate_presigned_url
            return generate_presigned_url(obj.minio_path)
        except Exception as e:
            print(f"⚠️ Failed to generate URL for {obj.minio_path}: {e}")
            return None
