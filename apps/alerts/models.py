from django.db import models
from apps.patients.models import Patient


class Alert(models.Model):
    ALERT_TYPES = [
        ('sepsis_risk', 'Sepsis Risk'),
        ('high_lactate', 'High Lactate'),
        ('hypotension', 'Hypotension'),
        ('tachycardia', 'Tachycardia'),
    ]

    STATUS = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS, default='active')

    risk_score = models.FloatField(null=True, blank=True)   # Se for IA ou modelo escore
    explanation = models.JSONField(null=True, blank=True)   # Explicabilidade (ex.: SHAP output)

    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['patient', 'status']),
        ]

    def __str__(self):
        return f"{self.get_alert_type_display()} for {self.patient} ({self.status})"
