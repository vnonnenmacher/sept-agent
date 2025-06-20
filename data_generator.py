import requests
import random
import time
import uuid
from faker import Faker
from datetime import datetime, timedelta, UTC

fake = Faker()

BASE_URL = "http://localhost:8000/fhir"

patients = []
episodes = {}

# ✅ Utilities
def now_iso():
    return datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')


def random_past_time(minutes=60):
    return (datetime.now(UTC) - timedelta(minutes=random.randint(1, minutes))).strftime('%Y-%m-%dT%H:%M:%SZ')


# =============================================
# 🚀 Patient & Episode Management
# =============================================

def create_patient():
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

    response = requests.post(f"{BASE_URL}/Patient/", json=payload)
    print(f"🧍 Patient {patient_id} → {response.status_code}: {response.text}")
    return patient_id


def start_episode(patient_id):
    open_episodes = [ep for ep in episodes[patient_id] if ep['open']]
    if open_episodes:
        print(f"🔄 Patient {patient_id} already has an open episode. Skipping start.")
        return None

    started_at = now_iso()

    payload = {
        "patient_id": patient_id,
        "startedAt": started_at
    }

    response = requests.post(f"{BASE_URL}/SepsisEpisode/start/", json=payload)
    if response.status_code in [200, 201]:
        episode_id = response.json().get('episode_id')
        episodes[patient_id].append({"id": episode_id, "start": started_at, "open": True})
        print(f"🚑 Episode {episode_id} for patient {patient_id} started.")
        return episode_id
    else:
        print(f"❌ Failed to start episode: {response.text}")
        return None


def close_episode(patient_id, episode):
    payload = {
        "episode_id": episode['id'],
        "endedAt": now_iso()
    }
    response = requests.post(f"{BASE_URL}/SepsisEpisode/close/", json=payload)
    if response.status_code in [200, 201]:
        episode['open'] = False
        print(f"🏁 Episode {episode['id']} for patient {patient_id} closed.")
    else:
        print(f"❌ Failed to close episode: {response.text}")


# =============================================
# 🚀 Clinical Events
# =============================================

def send_vitals(patient_id, episode_id):
    observed_at = now_iso()
    payload = {
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": observed_at,
        "resourceType": "Observation",
        "status": "final",
        "category": [{"coding": [{"code": "vital-signs"}]}],
        "code": {"coding": [{"code": "85354-9", "display": "Vitals"}]},
        "component": [
            {"code": {"coding": [{"code": "8480-6"}]}, "valueQuantity": {"value": random.randint(80, 160)}},
            {"code": {"coding": [{"code": "8462-4"}]}, "valueQuantity": {"value": random.randint(50, 100)}},
            {"code": {"coding": [{"code": "8867-4"}]}, "valueQuantity": {"value": random.randint(60, 130)}},
            {"code": {"coding": [{"code": "9279-1"}]}, "valueQuantity": {"value": random.randint(12, 28)}},
            {"code": {"coding": [{"code": "8310-5"}]}, "valueQuantity": {"value": round(random.uniform(36, 40), 1)}},
            {"code": {"coding": [{"code": "59408-5"}]}, "valueQuantity": {"value": random.randint(88, 100)}}
        ]
    }
    response = requests.post(f"{BASE_URL}/Vitals/", json=payload)
    print(f"📈 Vitals for {patient_id} → {response.status_code}")


def send_lab(patient_id, exam):
    observed_at = now_iso()
    value = exam['generator']()
    payload = {
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": observed_at,
        "resourceType": "Observation",
        "status": "final",
        "category": [{"coding": [{"code": "laboratory"}]}],
        "code": {"coding": [{"code": exam['code'], "display": exam['name']}]},
        "valueQuantity": {
            "value": value,
            "unit": exam['unit']
        }
    }
    response = requests.post(f"{BASE_URL}/LabResult/", json=payload)
    print(f"🧪 Lab {exam['name']} for patient {patient_id} → {response.status_code}")


def send_culture(patient_id):
    observed_at = now_iso()
    material = random.choice(["Blood", "Urine", "Sputum", "CSF"])

    payload = {
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": observed_at,
        "bodySite": {"text": material},
        "valueCodeableConcept": {
            "text": random.choice(["positive", "negative"])
        },
        "resourceType": "Observation",
        "status": "final",
        "category": [{"coding": [{"code": "laboratory"}]}],
        "code": {"coding": [{"code": "culture", "display": "Culture"}]}
    }
    response = requests.post(f"{BASE_URL}/Culture/", json=payload)
    print(f"🧫 Culture for {patient_id} ({material}) → {response.status_code}")


def send_antibiogram(patient_id, organism):
    observed_at = now_iso()

    antibiotics = ["Amoxicillin", "Ciprofloxacin", "Ceftriaxone", "Meropenem", "Vancomycin"]
    results = ["Susceptible", "Intermediate", "Resistant"]

    payload = {
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": observed_at,
        "valueCodeableConcept": {"text": organism},
        "resourceType": "Observation",
        "status": "final",
        "category": [{"coding": [{"code": "laboratory"}]}],
        "code": {"coding": [{"code": "18769-0", "display": "Antibiotic susceptibility panel"}]},
        "component": []
    }

    for ab in antibiotics:
        payload["component"].append({
            "code": {"coding": [{"display": ab}]},
            "valueCodeableConcept": {"text": random.choice(results)}
        })

    response = requests.post(f"{BASE_URL}/Antibiogram/", json=payload)
    print(f"🦠 Antibiogram for {patient_id} → {response.status_code}")


def send_antibiotic(patient_id):
    started_at = random_past_time(60)
    payload = {
        "subject": {"reference": f"Patient/{patient_id}"},
        "medicationCodeableConcept": {"text": random.choice(["Meropenem", "Ceftriaxone", "Ciprofloxacin"])},
        "effectivePeriod": {"start": started_at},
        "dosage": [{"text": "1g IV q8h"}],
        "route": {"text": "IV"}
    }
    response = requests.post(f"{BASE_URL}/AntibioticAdministration/", json=payload)
    print(f"💉 Antibiotic for {patient_id} → {response.status_code}")


def send_note(patient_id):
    content = random.choice([
        "Patient remains febrile. Monitoring cultures.",
        "Antibiotics adjusted based on antibiogram.",
        "Vitals improving. Plan to step down.",
        "Lactate downtrending. Hemodynamics stable.",
        "Awaiting blood culture results."
    ])
    payload = {
        "subject": {"reference": f"Patient/{patient_id}"},
        "date": now_iso(),
        "content": [{"text": {"div": content}}]
    }
    response = requests.post(f"{BASE_URL}/ClinicalNote/", json=payload)
    print(f"📝 Note for {patient_id} → {response.status_code}")


# =============================================
# 🚀 Main Loop
# =============================================

lab_catalog = [
    {"name": "CRP", "code": "1988-5", "unit": "mg/L", "generator": lambda: round(random.uniform(5, 300), 1)},
    {"name": "Procalcitonin", "code": "33959-8", "unit": "ng/mL", "generator": lambda: round(random.uniform(0.1, 20), 2)},
    {"name": "Creatinine", "code": "2160-0", "unit": "mg/dL", "generator": lambda: round(random.uniform(0.5, 5), 2)},
    {"name": "AST", "code": "1920-8", "unit": "U/L", "generator": lambda: random.randint(20, 500)},
    {"name": "ALT", "code": "1742-6", "unit": "U/L", "generator": lambda: random.randint(20, 500)},
    {"name": "Glucose", "code": "2345-7", "unit": "mg/dL", "generator": lambda: random.randint(70, 250)},
]

while True:
    action = random.choices(
        ["new_patient", "new_episode", "clinical_event"],
        weights=[0.05, 0.2, 0.75]
    )[0]

    if action == "new_patient" or not patients:
        patient_id = create_patient()
        start_episode(patient_id)

    elif action == "new_episode":
        patient_id = random.choice(patients)
        start_episode(patient_id)

    elif action == "clinical_event":
        patient_id = random.choice(patients)
        open_episodes = [ep for ep in episodes[patient_id] if ep['open']]
        if not open_episodes:
            start_episode(patient_id)
            continue

        episode = random.choice(open_episodes)

        event = random.choice(["vitals", "lab", "culture", "antibiogram", "antibiotic", "note"])
        if event == "vitals":
            send_vitals(patient_id, episode['id'])
        elif event == "lab":
            send_lab(patient_id, random.choice(lab_catalog))
        elif event == "culture":
            send_culture(patient_id)
        elif event == "antibiogram":
            send_antibiogram(patient_id, random.choice(["E. coli", "K. pneumoniae", "P. aeruginosa"]))
        elif event == "antibiotic":
            send_antibiotic(patient_id)
        elif event == "note":
            send_note(patient_id)

        if random.random() < 0.05:
            close_episode(patient_id, episode)

    time.sleep(5)
