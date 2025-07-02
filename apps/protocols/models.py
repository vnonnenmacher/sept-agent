from django.db import models


class KnowledgeDocument(models.Model):
    CATEGORY_CHOICES = [
        ("infection_protocol", "Infection Protocol"),
        ("institutional_protocol", "Institutional Protocol"),
        ("governmental_protocol", "Governmental Protocol"),
        ("flowchart", "Flowchart"),  # ← this is the correct English for "Fluxograma"
        ("other", "Other"),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    version = models.CharField(max_length=50)
    minio_path = models.CharField(max_length=255, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
