from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.patients.models import Patient
from django.utils.dateparse import parse_datetime
from apps.vitals.models import VitalsObservation
from apps.labs.models import LabResult


class FHIRPatientIngestionView(APIView):
    """
    Endpoint to receive FHIR Patient resource via webhook.
    """

    def post(self, request):
        data = request.data

        try:
            # Extract patient ID
            patient_id = data.get('id')
            if not patient_id:
                return Response({"error": "Missing 'id' field in Patient resource."}, status=400)

            # Extract name
            name_data = data.get('name', [])
            if name_data and isinstance(name_data, list):
                given = " ".join(name_data[0].get('given', []))
                family = name_data[0].get('family', '')
                full_name = f"{given} {family}".strip()
            else:
                full_name = "Unknown"

            # Extract gender
            gender = data.get('gender', 'unknown')

            # Extract birth date
            birth_date = data.get('birthDate', None)

            # Create or update patient
            patient, created = Patient.objects.update_or_create(
                patient_id=patient_id,
                defaults={
                    'name': full_name,
                    'gender': gender,
                    'birth_date': birth_date
                }
            )

            return Response({
                "status": "created" if created else "updated",
                "patient_id": patient.patient_id
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FHIRObservationIngestionView(APIView):
    """
    Ingest any FHIR Observation:
    - Vital signs (component-based)
    - Lab results (valueQuantity)
    - Antibiograms (component-based with organism)
    """

    def post(self, request):
        data = request.data

        try:
            # ✅ Patient
            subject = data.get('subject', {}).get('reference')
            if not subject or not subject.startswith('Patient/'):
                return Response({"error": "Missing or invalid 'subject' reference."}, status=400)
            patient_id = subject.split('/')[-1]
            patient, _ = Patient.objects.get_or_create(patient_id=patient_id)

            # ✅ Observation time
            observed_at = parse_datetime(data.get('effectiveDateTime'))
            if not observed_at:
                return Response({"error": "Missing or invalid 'effectiveDateTime'."}, status=400)

            # ✅ Observation category
            try:
                category = data.get('category', [])[0]['coding'][0]['code']
            except Exception:
                return Response({"error": "Missing 'category'."}, status=400)

            # ✅ Observation code
            observation_code = data.get('code', {}).get('coding', [{}])[0].get('code', '')

            # 🔥 ANTIBIOGRAM DETECTION (laboratory + code == 18769-0)
            if category == 'laboratory' and observation_code == '18769-0' and 'component' in data:
                organism = data.get('valueCodeableConcept', {}).get('text', 'Unknown organism')

                created = 0
                for comp in data.get('component', []):
                    antibiotic = comp['code']['coding'][0]['display']
                    result = comp.get('valueCodeableConcept', {}).get('text')

                    if not (antibiotic and result):
                        continue

                    LabResult.objects.create(
                        patient=patient,
                        exam_code="ANTIBIOGRAM",
                        exam_name=f"Antibiogram - {antibiotic}",
                        value=result,
                        unit=None,
                        observed_at=observed_at,
                        additional_info={"organism": organism, "antibiotic": antibiotic}
                    )
                    created += 1

                if created == 0:
                    return Response({"error": "No valid antibiogram components processed."}, status=400)

                return Response({"status": f"{created} antibiogram results recorded"}, status=201)

            # 🔥 VITAL SIGNS (vital-signs + component[])
            elif category == 'vital-signs' and 'component' in data:
                components = data.get('component', [])
                vitals_data = {}

                for comp in components:
                    code = comp['code']['coding'][0]['code']
                    value = comp.get('valueQuantity', {}).get('value')

                    if value is None:
                        continue

                    if code == '8480-6':
                        vitals_data['blood_pressure_sys'] = value
                    elif code == '8462-4':
                        vitals_data['blood_pressure_dia'] = value
                    elif code == '8867-4':
                        vitals_data['heart_rate'] = value
                    elif code == '9279-1':
                        vitals_data['respiratory_rate'] = value
                    elif code == '8310-5':
                        vitals_data['temperature'] = value
                    elif code == '59408-5':
                        vitals_data['oxygen_saturation'] = value

                if not vitals_data:
                    return Response({"error": "No valid vital signs components."}, status=400)

                VitalsObservation.objects.create(
                    patient=patient,
                    observed_at=observed_at,
                    **vitals_data
                )

                return Response({"status": "vitals recorded"}, status=201)

            # 🔥 SIMPLE LAB RESULT (laboratory + valueQuantity)
            elif category == 'laboratory' and 'valueQuantity' in data:
                LabResult.objects.create(
                    patient=patient,
                    exam_code=data['code']['coding'][0]['code'],
                    exam_name=data['code']['coding'][0]['display'],
                    value=data['valueQuantity']['value'],
                    unit=data['valueQuantity'].get('unit'),
                    observed_at=observed_at
                )

                return Response({"status": "lab result recorded"}, status=201)

            else:
                return Response(
                    {"error": "Unsupported observation format or missing components/valueQuantity."},
                    status=400
                )

        except Exception as e:
            return Response({"error": str(e)}, status=400)
