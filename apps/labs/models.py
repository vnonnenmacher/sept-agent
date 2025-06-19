from django.db import models
from apps.patients.models import Patient


class LabResult(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='labs')
    exam_code = models.CharField(max_length=50)        # "ANTIBIOGRAM"
    exam_name = models.CharField(max_length=255)       # Antibiogram - Antibiotic Name
    value = models.CharField(max_length=50)            # S / I / R
    unit = models.CharField(max_length=50, null=True, blank=True)
    observed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    additional_info = models.JSONField(null=True, blank=True)  # Organism, etc.

    def __str__(self):
        return f"{self.exam_name} for {self.patient} at {self.observed_at}"
