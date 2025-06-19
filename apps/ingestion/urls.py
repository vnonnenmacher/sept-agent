from django.urls import path
from apps.ingestion.views import FHIRObservationIngestionView, FHIRPatientIngestionView

urlpatterns = [
    path('fhir/Patient/', FHIRPatientIngestionView.as_view(), name='fhir-patient-ingest'),
    path('fhir/Observation/', FHIRObservationIngestionView.as_view(), name='fhir-observation-ingest'),
]
