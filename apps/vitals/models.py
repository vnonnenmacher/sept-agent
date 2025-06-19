from django.db import models
from apps.patients.models import Patient


class VitalsObservation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vitals')
    
    heart_rate = models.IntegerField(null=True, blank=True)               # BPM
    respiratory_rate = models.IntegerField(null=True, blank=True)         # RPM
    temperature = models.FloatField(null=True, blank=True)                # Celsius
    blood_pressure_sys = models.IntegerField(null=True, blank=True)       # mmHg
    blood_pressure_dia = models.IntegerField(null=True, blank=True)       # mmHg
    oxygen_saturation = models.IntegerField(null=True, blank=True)        # %

    observed_at = models.DateTimeField()                                  # Quando foi medido
    created_at = models.DateTimeField(auto_now_add=True)                  # Quando foi salvo no sistema

    class Meta:
        ordering = ['-observed_at']
        indexes = [
            models.Index(fields=['patient', 'observed_at']),
        ]

    def __str__(self):
        return f"Vitals for {self.patient} at {self.observed_at}"
