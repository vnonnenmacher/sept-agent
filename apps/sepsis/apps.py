from django.apps import AppConfig


class SepsisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sepsis'

    def ready(self):
        import apps.sepsis.signals
