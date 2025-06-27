from celery import shared_task
from apps.embeddings.vector_pipeline import (
    process_embedding,
    generate_patient_payload,
    generate_episode_payload,
    generate_culture_payload,
    generate_organism_payload,
    generate_antibiogram_payload,
    generate_antibiotic_payload,
    generate_vitals_payload,
    generate_lab_payload,
    generate_clinical_note_payload
)

from apps.patients.models import Patient
from apps.sepsis.models import (
    SepsisEpisode,
    CultureResult,
    Organism,
    VitalsObservation,
    LabResult,
    Antibiogram,
    AntibioticAdministration,
    ClinicalNote
)


@shared_task
def embed_patient_task(patient_id):
    try:
        patient = Patient.objects.get(patient_id=patient_id)
        print(f"🚀 Embedding Patient {patient_id}")
        process_embedding(generate_patient_payload(patient))
    except Patient.DoesNotExist:
        print(f"❌ Patient {patient_id} not found.")


@shared_task
def embed_episode_task(episode_id):
    try:
        episode = SepsisEpisode.objects.get(id=episode_id)
        print(f"🚀 Embedding Episode {episode_id}")
        process_embedding(generate_episode_payload(episode))
    except SepsisEpisode.DoesNotExist:
        print(f"❌ Episode {episode_id} not found.")


@shared_task
def embed_culture_task(culture_id):
    try:
        culture = CultureResult.objects.get(id=culture_id)
        print(f"🚀 Embedding Culture {culture_id}")
        process_embedding(generate_culture_payload(culture))
    except CultureResult.DoesNotExist:
        print(f"❌ Culture {culture_id} not found.")


@shared_task
def embed_organism_task(organism_id):
    try:
        organism = Organism.objects.get(id=organism_id)
        print(f"🚀 Embedding Organism {organism_id}")
        process_embedding(generate_organism_payload(organism))
    except Organism.DoesNotExist:
        print(f"❌ Organism {organism_id} not found.")


@shared_task
def embed_antibiogram_task(antibiogram_id):
    try:
        antibiogram = Antibiogram.objects.get(id=antibiogram_id)
        print(f"🚀 Embedding Antibiogram {antibiogram_id}")
        process_embedding(generate_antibiogram_payload(antibiogram))
    except Antibiogram.DoesNotExist:
        print(f"❌ Antibiogram {antibiogram_id} not found.")


@shared_task
def embed_antibiotic_task(administration_id):
    try:
        administration = AntibioticAdministration.objects.get(id=administration_id)
        print(f"🚀 Embedding Antibiotic {administration_id}")
        process_embedding(generate_antibiotic_payload(administration))
    except AntibioticAdministration.DoesNotExist:
        print(f"❌ Antibiotic {administration_id} not found.")


@shared_task
def embed_vitals_task(vitals_id):
    try:
        vitals = VitalsObservation.objects.get(id=vitals_id)
        print(f"🚀 Embedding Vitals {vitals_id}")
        process_embedding(generate_vitals_payload(vitals))
    except VitalsObservation.DoesNotExist:
        print(f"❌ Vitals {vitals_id} not found.")


@shared_task
def embed_lab_task(lab_id):
    try:
        lab = LabResult.objects.get(id=lab_id)
        print(f"🚀 Embedding Lab {lab_id}")
        process_embedding(generate_lab_payload(lab))
    except LabResult.DoesNotExist:
        print(f"❌ Lab {lab_id} not found.")


@shared_task
def embed_clinical_note_task(note_id):
    try:
        note = ClinicalNote.objects.get(id=note_id)
        print(f"🚀 Embedding Clinical Note {note_id}")
        process_embedding(generate_clinical_note_payload(note))
    except ClinicalNote.DoesNotExist:
        print(f"❌ Clinical Note {note_id} not found.")
