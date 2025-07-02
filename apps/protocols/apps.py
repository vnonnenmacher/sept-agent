from django.apps import AppConfig


class ProtocolsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.protocols'

    def ready(self):
        from .sync_documents import sync_documents_from_minio
        # sync_documents_from_minio()
