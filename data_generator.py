import requests
import random
import time
import uuid
from faker import Faker
from datetime import datetime, UTC

fake = Faker()

# ✅ API endpoint base URL
BASE_URL = "http://localhost:8000/fhir"

# ✅ List of generated patient IDs to reuse
patient_ids = []

# ✅ Utility to generate ISO UTC timestamp
def now_iso():
    return datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')


# 🚀 Generate and send a Patient
def send_patient():
    patient_id = str(uuid.uuid4())[:8]
    patient_ids.append(patient_id)

    payload = {
        "resourceType": "Patient",
        "id": patient_id,
        "name": [
            {
                "family": fake.last_name(),
                "given": [fake.first_name()]
            }
        ],
        "gender": random.choice(["male", "female", "unknown"]),
        "birthDate": fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat()
    }

    response = requests.post(f"{BASE_URL}/Patient/", json=payload)
    print(f"🧍 Patient {patient_id} → {response.status_code}: {response.text}")


# 🚀 Generate and send a Vitals Observation
def send_vitals():
    if not patient_ids:
        send_patient()

    patient_id = random.choice(patient_ids)
    observed_at = now_iso()

    payload = {
        "resourceType": "Observation",
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "85354-9",
                "display": "Vital Signs Panel"
            }]
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": observed_at,
        "component": [
            {
                "code": {"coding": [{"code": "8480-6", "display": "Systolic BP"}]},
                "valueQuantity": {"value": random.randint(100, 160), "unit": "mmHg"}
            },
            {
                "code": {"coding": [{"code": "8462-4", "display": "Diastolic BP"}]},
                "valueQuantity": {"value": random.randint(60, 100), "unit": "mmHg"}
            },
            {
                "code": {"coding": [{"code": "8867-4", "display": "Heart Rate"}]},
                "valueQuantity": {"value": random.randint(60, 120), "unit": "beats/minute"}
            },
            {
                "code": {"coding": [{"code": "9279-1", "display": "Respiratory Rate"}]},
                "valueQuantity": {"value": random.randint(12, 24), "unit": "breaths/minute"}
            },
            {
                "code": {"coding": [{"code": "8310-5", "display": "Temperature"}]},
                "valueQuantity": {"value": round(random.uniform(36.0, 39.0), 1), "unit": "C"}
            },
            {
                "code": {"coding": [{"code": "59408-5", "display": "Oxygen Saturation"}]},
                "valueQuantity": {"value": random.randint(90, 100), "unit": "%"}
            }
        ]
    }

    response = requests.post(f"{BASE_URL}/Observation/", json=payload)
    print(f"📈 Vitals for {patient_id} → {response.status_code}: {response.text}")


# 🚀 Generate and send a Lab Observation (like Lactate)
def send_lab():
    if not patient_ids:
        send_patient()

    patient_id = random.choice(patient_ids)
    observed_at = now_iso()

    payload = {
        "resourceType": "Observation",
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "laboratory",
                "display": "Laboratory"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "2524-7",
                "display": "Lactate"
            }]
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": observed_at,
        "valueQuantity": {
            "value": round(random.uniform(0.5, 5.0), 2),
            "unit": "mmol/L"
        }
    }

    response = requests.post(f"{BASE_URL}/Observation/", json=payload)
    print(f"🧪 Lab for {patient_id} → {response.status_code}: {response.text}")


# 🚀 Generate and send an Antibiogram
def send_antibiogram():
    if not patient_ids:
        send_patient()

    patient_id = random.choice(patient_ids)
    observed_at = now_iso()

    organism = random.choice([
        "Escherichia coli", "Klebsiella pneumoniae", "Pseudomonas aeruginosa", 
        "Staphylococcus aureus", "Enterococcus faecalis"
    ])

    antibiotics = [
        {"code": "372687004", "display": "Amoxicillin"},
        {"code": "372697008", "display": "Ciprofloxacin"},
        {"code": "372713005", "display": "Ceftriaxone"},
        {"code": "372692006", "display": "Meropenem"},
        {"code": "372698003", "display": "Vancomycin"},
    ]

    sus_results = ["Susceptible", "Intermediate", "Resistant"]

    payload = {
        "resourceType": "Observation",
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "laboratory",
                "display": "Laboratory"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "18769-0",
                "display": "Antibiotic susceptibility panel"
            }]
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": observed_at,
        "valueCodeableConcept": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "112283007",
                "display": organism
            }],
            "text": organism
        },
        "component": []
    }

    for ab in antibiotics:
        result = random.choice(sus_results)
        payload["component"].append({
            "code": {
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": ab["code"],
                    "display": ab["display"]
                }]
            },
            "valueCodeableConcept": {
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": result[0].upper(),  # S, I, R
                    "display": result
                }],
                "text": result
            }
        })

    response = requests.post(f"{BASE_URL}/Observation/", json=payload)
    print(f"🦠 Antibiogram for {patient_id} ({organism}) → {response.status_code}: {response.text}")


# 🔁 Main Loop
while True:
    action = random.choice(["patient", "vitals", "lab", "antibiogram"])

    if action == "patient":
        send_patient()
    elif action == "vitals":
        send_vitals()
    elif action == "lab":
        send_lab()
    elif action == "antibiogram":
        send_antibiogram()

    time.sleep(5)
