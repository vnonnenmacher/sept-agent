import requests
import random
import time
import uuid
from faker import Faker
from datetime import datetime, timedelta, UTC

from django.core.management.base import BaseCommand

fake = Faker('pt_BR')

BASE_URL = "http://localhost:8000/fhir"

patients = []
episodes = {}

# ✅ Utilities
def now_iso():
    return datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')

def random_past_time(minutes=60):
    return (datetime.now(UTC) - timedelta(minutes=random.randint(1, minutes))).strftime('%Y-%m-%dT%H:%M:%SZ')

# ==========================================================
# 🚀 Command
# ==========================================================

class Command(BaseCommand):
    help = "Simula um HIS enviando dados de sepse via API"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Iniciando Simulação do HIS"))

        while True:
            try:
                self.simulate_interaction()
                time.sleep(5)  # Intervalo entre eventos
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Exceção: {e}"))
                time.sleep(5)

    # ==========================================================
    # 🚑 Main Simulation Logic
    # ==========================================================

    def simulate_interaction(self):
        if random.random() < 0.5 or not patients:
            patient_id = self.create_patient()
            episode_id = self.start_episode(patient_id)
            if episode_id:
                self.send_vitals(patient_id, episode_id)
                if random.random() < 0.3:
                    self.send_note(patient_id)
            return

        patient_id = random.choice(patients)
        open_eps = [ep for ep in episodes[patient_id] if ep['open']]

        if not open_eps:
            if random.random() < 0.2:
                episode_id = self.start_episode(patient_id)
                if episode_id:
                    self.send_antibiotic(patient_id)
                    self.send_vitals(patient_id, episode_id)
                    if random.random() < 0.3:
                        self.send_note(patient_id)
            return

        episode = open_eps[0]
        episode_id = episode['id']

        if random.random() < 0.6:
            result = random.choice(["positive", "negative"])
            self.send_culture(patient_id, result)
            if result == "negative":
                self.close_episode(patient_id, episode)
                return

            organism = random.choice(["E. coli", "K. pneumoniae", "P. aeruginosa"])
            self.send_antibiogram(patient_id, organism)

        self.send_antibiotic(patient_id)
        self.send_vitals(patient_id, episode_id)

        if random.random() < 0.5:
            self.send_note(patient_id)

    # ==========================================================
    # 🧍 Patient and Episode Management
    # ==========================================================

    def create_patient(self):
        patient_id = str(uuid.uuid4())[:8]
        patients.append(patient_id)
        episodes[patient_id] = []

        payload = {
            "resourceType": "Patient",
            "id": patient_id,
            "name": [{
                "family": fake.last_name(),
                "given": [fake.first_name()]
            }],
            "gender": random.choice(["male", "female", "unknown"]),
            "birthDate": fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat()
        }

        r = requests.post(f"{BASE_URL}/Patient/", json=payload)
        print(f"🧍 Paciente {patient_id} → {r.status_code}: {r.text}")
        return patient_id

    def start_episode(self, patient_id):
        open_eps = [ep for ep in episodes[patient_id] if ep['open']]
        if open_eps:
            print(f"🔄 Paciente {patient_id} já possui episódio aberto.")
            return None

        started_at = now_iso()

        payload = {
            "patient_id": patient_id,
            "startedAt": started_at
        }

        r = requests.post(f"{BASE_URL}/SepsisEpisode/start/", json=payload)
        if r.status_code in [200, 201]:
            episode_id = r.json().get('episode_id')
            episodes[patient_id].append({"id": episode_id, "start": started_at, "open": True})
            print(f"🚑 Episódio {episode_id} para paciente {patient_id} iniciado.")
            return episode_id
        else:
            print(f"❌ Falha ao iniciar episódio: {r.text}")
            return None

    def close_episode(self, patient_id, episode):
        payload = {
            "episode_id": episode['id'],
            "endedAt": now_iso()
        }
        r = requests.post(f"{BASE_URL}/SepsisEpisode/close/", json=payload)
        if r.status_code in [200, 201]:
            episode['open'] = False
            print(f"🏁 Episódio {episode['id']} para paciente {patient_id} encerrado.")
        else:
            print(f"❌ Falha ao encerrar episódio: {r.text}")

    # ==========================================================
    # 🚨 Clinical Events
    # ==========================================================

    def send_vitals(self, patient_id, episode_id):
        payload = {
            "subject": {"reference": f"Patient/{patient_id}"},
            "effectiveDateTime": now_iso(),
            "component": [
                {"code": {"coding": [{"code": "8480-6"}]}, "valueQuantity": {"value": random.randint(90, 160)}},  # Sistólica
                {"code": {"coding": [{"code": "8462-4"}]}, "valueQuantity": {"value": random.randint(50, 100)}},  # Diastólica
                {"code": {"coding": [{"code": "8867-4"}]}, "valueQuantity": {"value": random.randint(60, 130)}},  # FC
                {"code": {"coding": [{"code": "9279-1"}]}, "valueQuantity": {"value": random.randint(12, 28)}},   # FR
                {"code": {"coding": [{"code": "8310-5"}]}, "valueQuantity": {"value": round(random.uniform(36, 40), 1)}},  # Temp
                {"code": {"coding": [{"code": "59408-5"}]}, "valueQuantity": {"value": random.randint(88, 100)}}  # SatO2
            ]
        }
        r = requests.post(f"{BASE_URL}/Vitals/", json=payload)
        print(f"📈 Sinais vitais para {patient_id} → {r.status_code}")

    def send_lab(self, patient_id):
        lab = random.choice([
            {"name": "PCR", "code": "1988-5", "unit": "mg/L", "value": round(random.uniform(5, 300), 1)},
            {"name": "Procalcitonina", "code": "33959-8", "unit": "ng/mL", "value": round(random.uniform(0.1, 20), 2)},
            {"name": "Creatinina", "code": "2160-0", "unit": "mg/dL", "value": round(random.uniform(0.5, 5), 2)},
        ])
        payload = {
            "subject": {"reference": f"Patient/{patient_id}"},
            "effectiveDateTime": now_iso(),
            "code": {"coding": [{"code": lab["code"], "display": lab["name"]}]},
            "valueQuantity": {
                "value": lab["value"],
                "unit": lab["unit"]
            }
        }
        r = requests.post(f"{BASE_URL}/LabResult/", json=payload)
        print(f"🧪 Exame {lab['name']} para {patient_id} → {r.status_code}")

    def send_culture(self, patient_id, result):
        payload = {
            "subject": {"reference": f"Patient/{patient_id}"},
            "effectiveDateTime": now_iso(),
            "bodySite": {"text": random.choice(["Sangue", "Urina", "LCR", "Escarro"])},
            "valueCodeableConcept": {"text": result},
            "component": []
        }

        if result == "positive":
            organism = random.choice(["E. coli", "K. pneumoniae", "P. aeruginosa"])
            payload["component"].append({
                "valueCodeableConcept": {"text": organism}
            })

        r = requests.post(f"{BASE_URL}/Culture/", json=payload)
        print(f"🧫 Cultura {result.upper()} para {patient_id} → {r.status_code}")

    def send_antibiogram(self, patient_id, organism):
        payload = {
            "subject": {"reference": f"Patient/{patient_id}"},
            "effectiveDateTime": now_iso(),
            "valueCodeableConcept": {"text": organism},
            "component": [
                {
                    "code": {"coding": [{"display": ab}]},
                    "valueCodeableConcept": {"text": random.choice(["Sensível", "Resistente", "Intermediário"])}
                }
                for ab in ["Amoxicilina", "Ceftriaxona", "Meropenem", "Vancomicina"]
            ]
        }
        r = requests.post(f"{BASE_URL}/Antibiogram/", json=payload)
        print(f"🦠 Antibiograma para {patient_id} organismo {organism} → {r.status_code}")

    def send_antibiotic(self, patient_id):
        payload = {
            "subject": {"reference": f"Patient/{patient_id}"},
            "medicationCodeableConcept": {"text": random.choice(["Ceftriaxona", "Meropenem", "Ciprofloxacino"])},
            "effectivePeriod": {
                "start": random_past_time(),
                "end": now_iso(),
            },
            "dosage": [{"text": "1g IV a cada 8h"}],
            "route": {"text": "Intravenoso"}
        }
        r = requests.post(f"{BASE_URL}/AntibioticAdministration/", json=payload)
        print(f"💉 Antibiótico para {patient_id} → {r.status_code}")

    def send_note(self, patient_id):
        payload = {
            "subject": {"reference": f"Patient/{patient_id}"},
            "date": now_iso(),
            "author": {"display": "Dr. IA"},
            "content": [{"text": {"div": random.choice([
                "Paciente está sendo monitorado.",
                "Aguardando resultado da cultura.",
                "Antibiótico ajustado conforme antibiograma.",
                "Paciente apresenta sinais de melhora."
            ])}}]
        }
        r = requests.post(f"{BASE_URL}/ClinicalNote/", json=payload)
        print(f"📝 Nota clínica para {patient_id} → {r.status_code}")
