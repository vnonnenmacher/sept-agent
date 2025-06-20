from celery import shared_task
from apps.embeddings.vector_pipeline import (
    embed_and_store_patient,
    embed_and_store_vitals,
    embed_and_store_lab,
    embed_and_store_antibiogram,
    embed_and_store_antibiotic,
    embed_and_store_clinical_note
)

from apps.patients.models import Patient
from apps.sepsis.models import (
    VitalsObservation,
    LabResult,
    Antibiogram,
    AntibioticAdministration,
    ClinicalNote
)


# 🚀 Patient
@shared_task
def embed_patient_task(patient_id):
    try:
        patient = Patient.objects.get(patient_id=patient_id)
        embed_and_store_patient(patient)
        print(f"✅ Patient {patient_id} embedded successfully.")
    except Patient.DoesNotExist:
        print(f"❌ Patient {patient_id} not found.")


# 🚀 Vitals
@shared_task
def embed_vitals_task(vitals_id):
    try:
        vitals = VitalsObservation.objects.get(id=vitals_id)
        embed_and_store_vitals(vitals)
        print(f"✅ Vitals {vitals_id} embedded successfully.")
    except VitalsObservation.DoesNotExist:
        print(f"❌ Vitals {vitals_id} not found.")


# 🚀 Labs (non-micro)
@shared_task
def embed_lab_task(lab_id):
    try:
        lab = LabResult.objects.get(id=lab_id)
        embed_and_store_lab(lab)
        print(f"✅ Lab {lab_id} embedded successfully.")
    except LabResult.DoesNotExist:
        print(f"❌ Lab {lab_id} not found.")


# 🚀 Antibiograms
@shared_task
def embed_antibiogram_task(antibiogram_id):
    try:
        antibiogram = Antibiogram.objects.get(id=antibiogram_id)
        embed_and_store_antibiogram(antibiogram)
        print(f"✅ Antibiogram {antibiogram_id} embedded successfully.")
    except Antibiogram.DoesNotExist:
        print(f"❌ Antibiogram {antibiogram_id} not found.")


# 🚀 Antibiotic Administration
@shared_task
def embed_antibiotic_task(administration_id):
    try:
        administration = AntibioticAdministration.objects.get(id=administration_id)
        embed_and_store_antibiotic(administration)
        print(f"✅ Antibiotic administration {administration_id} embedded successfully.")
    except AntibioticAdministration.DoesNotExist:
        print(f"❌ Antibiotic administration {administration_id} not found.")


# 🚀 Clinical Notes
@shared_task
def embed_clinical_note_task(note_id):
    try:
        note = ClinicalNote.objects.get(id=note_id)
        embed_and_store_clinical_note(note)
        print(f"✅ Clinical note {note_id} embedded successfully.")
    except ClinicalNote.DoesNotExist:
        print(f"❌ Clinical note {note_id} not found.")
