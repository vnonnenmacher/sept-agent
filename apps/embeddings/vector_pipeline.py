from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import uuid


# ✅ Qdrant Client e Modelo
client = QdrantClient("qdrant", port=6333)
model = SentenceTransformer('pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb')


# ✅ Collection
def create_collection_if_not_exists(collection_name="clinical-data"):
    if not client.collection_exists(collection_name=collection_name):
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=384,
                distance=models.Distance.COSINE
            )
        )
        print(f"✅ Collection '{collection_name}' criada.")
    else:
        print(f"✔️ Collection '{collection_name}' já existe.")


# ===============================================================
# 🚀 Função Genérica de Processamento
# ===============================================================
def process_embedding(payload: dict):
    create_collection_if_not_exists()

    embedding = model.encode(payload["text"]).tolist()

    point_id = f"{payload['type']}_{payload.get('patient_id') or payload.get('episode_id') or payload.get('culture_id') or payload.get('organism_id') or payload.get('vitals_id') or payload.get('lab_id') or payload.get('antibiogram_id') or payload.get('administration_id') or payload.get('note_id') or uuid.uuid4()}"

    point = models.PointStruct(
        id=point_id,
        vector=embedding,
        payload=payload
    )

    client.upsert(collection_name="clinical-data", points=[point])
    print(f"✅ Embedded {payload['type']} → {payload.get('patient_id', '')}")


# ===============================================================
# 🚀 Funções de Geração de Payload — Cada Evento
# ===============================================================


def generate_patient_payload(patient):
    text = (
        f"O paciente {patient.name}, gênero {patient.gender}, nascido em {patient.birth_date}, "
        "foi admitido no sistema hospitalar para monitoramento e acompanhamento clínico."
    )
    return {
        "type": "patient",
        "patient_id": patient.patient_id,
        "name": patient.name,
        "gender": patient.gender,
        "birth_date": str(patient.birth_date),
        "text": text
    }


def generate_episode_payload(episode):
    text = (
        f"O paciente {episode.patient.name} foi incluído no protocolo de sepse em {episode.started_at}. "
        "Este evento indica que há suspeita clínica ou confirmação de sepse, iniciando acompanhamento intensivo e intervenções terapêuticas."
    )
    return {
        "type": "sepsis_episode",
        "episode_id": episode.id,
        "patient_id": episode.patient.patient_id,
        "started_at": str(episode.started_at),
        "ended_at": str(episode.ended_at) if episode.ended_at else None,
        "text": text
    }


def generate_culture_payload(culture):
    text = (
        f"Foi realizada uma cultura microbiológica do material {culture.sample.material} na data {culture.reported_at}. "
        f"O resultado da cultura foi {culture.result.upper()}, indicando "
        f"{'presença de infecção bacteriana' if culture.result.lower() == 'positive' else 'ausência de crescimento bacteriano'} "
        "no material coletado."
    )
    return {
        "type": "culture_result",
        "culture_id": culture.id,
        "episode_id": culture.sample.episode.id,
        "patient_id": culture.sample.episode.patient.patient_id,
        "result": culture.result,
        "material": culture.sample.material,
        "reported_at": str(culture.reported_at),
        "text": text
    }


def generate_organism_payload(organism):
    text = (
        f"O organismo {organism.name} foi identificado na cultura microbiológica do paciente. "
        "Este achado confirma a presença desse microrganismo como agente causador da infecção no paciente."
    )
    return {
        "type": "organism",
        "organism_id": organism.id,
        "culture_id": organism.culture_result.id,
        "episode_id": organism.culture_result.sample.episode.id,
        "patient_id": organism.culture_result.sample.episode.patient.patient_id,
        "name": organism.name,
        "text": text
    }


def generate_antibiogram_payload(antibiogram):
    organism = antibiogram.organism.name
    sus_results = [
        f"{sus.antibiotic} é {sus.result.lower()}"
        for sus in antibiogram.susceptibilities.all()
    ]
    text = (
        f"Foi realizado um antibiograma para avaliar a sensibilidade do organismo {organism} identificado na cultura. "
        "Os resultados são: " + ", ".join(sus_results) + ". "
        "Essas informações orientam a escolha do antibiótico mais adequado para o tratamento da infecção."
    )
    return {
        "type": "antibiogram",
        "antibiogram_id": antibiogram.id,
        "organism": organism,
        "episode_id": antibiogram.organism.culture_result.sample.episode.id,
        "patient_id": antibiogram.organism.culture_result.sample.episode.patient.patient_id,
        "text": text
    }


def generate_antibiotic_payload(administration):
    status = "em andamento" if not administration.stopped_at else "finalizado"
    text = (
        f"O paciente recebeu administração do antibiótico {administration.name} "
        f"{status}. Início em {administration.started_at}, dose {administration.dose or 'não informada'}, via {administration.route or 'não informada'}. "
        "Esse antibiótico foi prescrito como parte do tratamento para infecção bacteriana."
    )
    return {
        "type": "antibiotic",
        "administration_id": administration.id,
        "episode_id": administration.episode.id,
        "patient_id": administration.episode.patient.patient_id,
        "text": text
    }


def generate_vitals_payload(vitals):
    observations = []

    if vitals.temperature:
        if vitals.temperature >= 38:
            observations.append(f"febre {vitals.temperature}ºC")
        elif vitals.temperature <= 36:
            observations.append(f"hipotermia {vitals.temperature}ºC")
        else:
            observations.append(f"temperatura normal {vitals.temperature}ºC")

    if vitals.heart_rate:
        if vitals.heart_rate >= 100:
            observations.append(f"taquicardia {vitals.heart_rate} bpm")
        elif vitals.heart_rate <= 60:
            observations.append(f"bradicardia {vitals.heart_rate} bpm")
        else:
            observations.append(f"frequência cardíaca normal {vitals.heart_rate} bpm")

    if vitals.respiratory_rate:
        if vitals.respiratory_rate >= 22:
            observations.append(f"taquipneia {vitals.respiratory_rate} rpm")
        else:
            observations.append(f"frequência respiratória normal {vitals.respiratory_rate} rpm")

    if vitals.blood_pressure_sys and vitals.blood_pressure_dia:
        if vitals.blood_pressure_sys <= 90:
            observations.append(f"hipotensão {vitals.blood_pressure_sys}/{vitals.blood_pressure_dia} mmHg")
        else:
            observations.append(f"pressão arterial {vitals.blood_pressure_sys}/{vitals.blood_pressure_dia} mmHg")

    if vitals.oxygen_saturation:
        if vitals.oxygen_saturation <= 94:
            observations.append(f"hipoxemia {vitals.oxygen_saturation}%")
        else:
            observations.append(f"saturação normal {vitals.oxygen_saturation}%")

    if not observations:
        observations.append("sinais vitais não informados")

    text = (
        f"Avaliação dos sinais vitais do paciente realizada em {vitals.observed_at}: "
        + ", ".join(observations) + ". "
        "Esses parâmetros são fundamentais para o monitoramento da gravidade clínica, estabilidade hemodinâmica e evolução do quadro infeccioso."
    )
    return {
        "type": "vitals",
        "vitals_id": vitals.id,
        "episode_id": vitals.episode.id,
        "patient_id": vitals.episode.patient.patient_id,
        "observed_at": str(vitals.observed_at),
        "text": text
    }


def generate_lab_payload(lab):
    text = (
        f"O exame laboratorial {lab.exam_name} foi realizado na data {lab.observed_at}, "
        f"apresentando valor de {lab.value} {lab.unit or ''}. "
        "Este exame contribui para a avaliação da condição clínica e acompanhamento da evolução do paciente."
    )
    return {
        "type": "lab_result",
        "lab_id": lab.id,
        "episode_id": lab.episode.id,
        "patient_id": lab.episode.patient.patient_id,
        "exam_name": lab.exam_name,
        "value": lab.value,
        "unit": lab.unit,
        "observed_at": str(lab.observed_at),
        "text": text
    }


def generate_clinical_note_payload(note):
    return {
        "type": "clinical_note",
        "note_id": note.id,
        "episode_id": note.episode.id,
        "patient_id": note.episode.patient.patient_id,
        "author": note.author,
        "created_at": str(note.created_at),
        "text": note.content
    }
