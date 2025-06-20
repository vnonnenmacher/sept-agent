from django.urls import path
from apps.ingestion.views import (
    FHIRPatientIngestionView,
    FHIROpenSepsisEpisodeView,
    FHIRCloseSepsisEpisodeView,
    FHIRCultureIngestionView,
    FHIRAntibiogramIngestionView,
    FHIRVitalsIngestionView,
    FHIRLabResultIngestionView,
    FHIRAntibioticAdministrationIngestionView,
    FHIRClinicalNoteIngestionView,
)

urlpatterns = [
    # ✅ Patient
    path('fhir/Patient/', FHIRPatientIngestionView.as_view(), name='fhir-patient-ingest'),

    # ✅ Sepsis Episode Lifecycle
    path('fhir/SepsisEpisode/start/', FHIROpenSepsisEpisodeView.as_view(), name='fhir-sepsis-episode-start'),
    path('fhir/SepsisEpisode/close/', FHIRCloseSepsisEpisodeView.as_view(), name='fhir-sepsis-episode-close'),

    # ✅ Microbiology
    path('fhir/Culture/', FHIRCultureIngestionView.as_view(), name='fhir-culture-ingest'),
    path('fhir/Antibiogram/', FHIRAntibiogramIngestionView.as_view(), name='fhir-antibiogram-ingest'),

    # ✅ Vitals
    path('fhir/Vitals/', FHIRVitalsIngestionView.as_view(), name='fhir-vitals-ingest'),

    # ✅ Non-Micro Labs
    path('fhir/LabResult/', FHIRLabResultIngestionView.as_view(), name='fhir-labresult-ingest'),

    # ✅ Antibiotics
    path('fhir/AntibioticAdministration/', FHIRAntibioticAdministrationIngestionView.as_view(), name='fhir-antibiotic-ingest'),

    # ✅ Clinical Notes
    path('fhir/ClinicalNote/', FHIRClinicalNoteIngestionView.as_view(), name='fhir-clinical-note-ingest'),
]
