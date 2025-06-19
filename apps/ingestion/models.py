from django.db import models


class IngestionLog(models.Model):
    source = models.CharField(max_length=100)          # De onde veio (ex.: 'EHR SQL', 'FHIR API')
    description = models.TextField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(auto_now=True)

    success = models.BooleanField(default=True)
    records_ingested = models.IntegerField(default=0)

    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Ingestion from {self.source} at {self.started_at}"
