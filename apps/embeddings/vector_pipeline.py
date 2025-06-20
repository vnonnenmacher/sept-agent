from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import uuid


# 🚀 Qdrant Client and Embedding Model
client = QdrantClient("qdrant", port=6333)
model = SentenceTransformer('all-MiniLM-L6-v2')


# 🚀 Ensure Collection Exists
def create_collection_if_not_exists(collection_name="clinical-data"):
    if not client.collection_exists(collection_name=collection_name):
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=384,
                distance=models.Distance.COSINE
            )
        )
        print(f"✅ Collection '{collection_name}' created.")
    else:
        print(f"✔️ Collection '{collection_name}' already exists.")

def generate_patient_text(patient):
    return f"Patient {patient.name}, gender {patient.gender}, born on {patient.birth_date}."


def embed_and_store_patient(patient):
    create_collection_if_not_exists()

    text = generate_patient_text(patient)
    embedding = model.encode(text).tolist()

    point = models.PointStruct(
        id=str(uuid.uuid4()),
        vector=embedding,
        payload={
            "type": "patient",
            "patient_id": patient.patient_id,
            "name": patient.name,
            "gender": patient.gender,
            "birth_date": str(patient.birth_date),
            "text": text
        }
    )

    client.upsert(collection_name="clinical-data", points=[point])
    print(f"✅ Embedded patient {patient.patient_id}")


def generate_vitals_text(vitals):
    observations = []

    if vitals.temperature:
        fever = "fever" if vitals.temperature >= 38 else "hypothermia" if vitals.temperature <= 36 else "normal temperature"
        observations.append(f"{fever} {vitals.temperature} Celsius")

    if vitals.heart_rate:
        hr_state = "tachycardia" if vitals.heart_rate >= 100 else "bradycardia" if vitals.heart_rate <= 60 else "normal heart rate"
        observations.append(f"{hr_state} {vitals.heart_rate} BPM")

    if vitals.respiratory_rate:
        rr_state = "tachypnea" if vitals.respiratory_rate >= 22 else "normal respiratory rate"
        observations.append(f"{rr_state} {vitals.respiratory_rate} RPM")

    if vitals.blood_pressure_sys and vitals.blood_pressure_dia:
        hypotension = "hypotension" if vitals.blood_pressure_sys <= 90 else "normal blood pressure"
        observations.append(f"{hypotension} {vitals.blood_pressure_sys}/{vitals.blood_pressure_dia} mmHg")

    if vitals.oxygen_saturation:
        o2_state = "hypoxia" if vitals.oxygen_saturation <= 94 else "normal oxygen saturation"
        observations.append(f"{o2_state} {vitals.oxygen_saturation}%")

    if not observations:
        observations.append("no vital signs recorded")

    return (
        f"Vitals for patient {vitals.episode.patient.patient_id} at {vitals.observed_at}: "
        + ", ".join(observations)
    )


def embed_and_store_vitals(vitals):
    create_collection_if_not_exists()

    text = generate_vitals_text(vitals)
    embedding = model.encode(text).tolist()

    point = models.PointStruct(
        id=str(uuid.uuid4()),
        vector=embedding,
        payload={
            "type": "vitals",
            "vitals_id": vitals.id,
            "episode_id": vitals.episode.id,
            "patient_id": vitals.episode.patient.patient_id,
            "observed_at": str(vitals.observed_at),
            "text": text
        }
    )

    client.upsert(collection_name="clinical-data", points=[point])
    print(f"✅ Embedded vitals {vitals.id}")


def generate_lab_text(lab):
    label = ""
    if lab.exam_name.lower() in ['crp', 'procalcitonin', 'leukocytes']:
        label = " (high)" if lab.value > 100 else " (normal)"  # example threshold

    return (
        f"Lab {lab.exam_name} observed at {lab.observed_at}: "
        f"value {lab.value} {lab.unit or ''}{label} for patient {lab.episode.patient.patient_id}."
    )


def embed_and_store_lab(lab):
    create_collection_if_not_exists()

    text = generate_lab_text(lab)
    embedding = model.encode(text).tolist()

    point = models.PointStruct(
        id=str(uuid.uuid4()),
        vector=embedding,
        payload={
            "type": "lab",
            "lab_id": lab.id,
            "episode_id": lab.episode.id,
            "patient_id": lab.episode.patient.patient_id,
            "exam_name": lab.exam_name,
            "value": lab.value,
            "unit": lab.unit,
            "observed_at": str(lab.observed_at),
            "text": text
        }
    )

    client.upsert(collection_name="clinical-data", points=[point])
    print(f"✅ Embedded lab {lab.id}")


def generate_antibiogram_text(antibiogram):
    organism = antibiogram.organism.name
    sus_results = []

    for sus in antibiogram.susceptibilities.all():
        sus_results.append(f"{sus.antibiotic} is {sus.result.lower()}")

    return (
        f"Antibiogram for patient {antibiogram.organism.culture_result.sample.episode.patient.patient_id}: "
        f"organism {organism}. " + ", ".join(sus_results) + "."
    )


def embed_and_store_antibiogram(antibiogram):
    create_collection_if_not_exists()

    text = generate_antibiogram_text(antibiogram)
    embedding = model.encode(text).tolist()

    point = models.PointStruct(
        id=str(uuid.uuid4()),
        vector=embedding,
        payload={
            "type": "antibiogram",
            "antibiogram_id": antibiogram.id,
            "organism": antibiogram.organism.name,
            "episode_id": antibiogram.organism.culture_result.sample.episode.id,
            "patient_id": antibiogram.organism.culture_result.sample.episode.patient.patient_id,
            "text": text
        }
    )

    client.upsert(collection_name="clinical-data", points=[point])
    print(f"✅ Embedded antibiogram {antibiogram.id}")


def generate_antibiotic_text(abx):
    status = "ongoing" if not abx.stopped_at else "completed"
    return (
        f"Antibiotic {abx.name} {status} for patient {abx.episode.patient.patient_id}. "
        f"Started at {abx.started_at}, dose {abx.dose or 'unknown'}, route {abx.route or 'unknown'}."
    )


def embed_and_store_antibiotic(administration):
    create_collection_if_not_exists()

    text = generate_antibiotic_text(administration)
    embedding = model.encode(text).tolist()

    point = models.PointStruct(
        id=str(uuid.uuid4()),
        vector=embedding,
        payload={
            "type": "antibiotic",
            "administration_id": administration.id,
            "episode_id": administration.episode.id,
            "patient_id": administration.episode.patient.patient_id,
            "text": text
        }
    )

    client.upsert(collection_name="clinical-data", points=[point])
    print(f"✅ Embedded antibiotic administration {administration.id}")


def embed_and_store_clinical_note(note):
    create_collection_if_not_exists()

    text = note.content
    embedding = model.encode(text).tolist()

    point = models.PointStruct(
        id=str(uuid.uuid4()),
        vector=embedding,
        payload={
            "type": "clinical_note",
            "note_id": note.id,
            "episode_id": note.episode.id,
            "patient_id": note.episode.patient.patient_id,
            "author": note.author,
            "created_at": str(note.created_at),
            "text": text
        }
    )

    client.upsert(collection_name="clinical-data", points=[point])
    print(f"✅ Embedded clinical note {note.id}")
