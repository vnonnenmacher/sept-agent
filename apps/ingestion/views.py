from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime

from apps.patients.models import Patient
from apps.sepsis.models import (
    SepsisEpisode,
    Sample,
    CultureResult,
    Organism,
    Antibiogram,
    AntibioticSusceptibility,
    VitalsObservation,
    LabResult,
    AntibioticAdministration,
    ClinicalNote
)


class FHIRPatientIngestionView(APIView):
    def post(self, request):
        data = request.data

        try:
            patient_id = data.get('id')
            if not patient_id:
                return Response({"error": "Missing 'id' field."}, status=400)

            name_data = data.get('name', [])
            given = " ".join(name_data[0].get('given', [])) if name_data else ""
            family = name_data[0].get('family', '') if name_data else ""
            full_name = f"{given} {family}".strip() or "Unknown"

            gender = data.get('gender', 'unknown')
            birth_date = data.get('birthDate', None)

            patient, created = Patient.objects.update_or_create(
                patient_id=patient_id,
                defaults={'name': full_name, 'gender': gender, 'birth_date': birth_date}
            )

            return Response({
                "status": "created" if created else "updated",
                "patient_id": patient.patient_id
            }, status=201 if created else 200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class FHIROpenSepsisEpisodeView(APIView):
    def post(self, request):
        try:
            patient_id = request.data.get('patient_id')
            started_at = parse_datetime(request.data.get('startedAt'))

            patient = Patient.objects.get(patient_id=patient_id)

            episode = SepsisEpisode.objects.create(
                patient=patient,
                started_at=started_at
            )

            return Response({"status": "episode opened", "episode_id": episode.id}, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class FHIRCloseSepsisEpisodeView(APIView):
    def post(self, request):
        try:
            episode_id = request.data.get('episode_id')
            ended_at = parse_datetime(request.data.get('endedAt'))

            episode = SepsisEpisode.objects.get(id=episode_id)
            episode.ended_at = ended_at
            episode.save()

            return Response({"status": "episode closed"}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class FHIRCultureIngestionView(APIView):
    def post(self, request):
        try:
            data = request.data
            patient_id = data.get('subject', {}).get('reference', '').split('/')[-1]
            patient = Patient.objects.get(patient_id=patient_id)

            episode = SepsisEpisode.objects.filter(patient=patient).order_by('-started_at').first()
            if not episode:
                return Response({"error": "No active episode."}, status=400)

            observed_at = parse_datetime(data.get('effectiveDateTime'))
            material = data.get('bodySite', {}).get('text', 'Unknown')

            sample, _ = Sample.objects.get_or_create(
                episode=episode,
                material=material,
                collected_at=observed_at
            )

            result = data.get('valueCodeableConcept', {}).get('text', '').lower()
            if result not in ['positive', 'negative']:
                return Response({"error": "Result must be 'positive' or 'negative'."}, status=400)

            culture = CultureResult.objects.create(
                sample=sample,
                result=result,
                reported_at=observed_at
            )

            if result == 'positive':
                for comp in data.get('component', []):
                    organism_name = comp.get('valueCodeableConcept', {}).get('text')
                    if organism_name:
                        Organism.objects.create(culture_result=culture, name=organism_name)

            return Response({"status": "culture recorded"}, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class FHIRAntibiogramIngestionView(APIView):
    def post(self, request):
        try:
            data = request.data
            patient_id = data.get('subject', {}).get('reference', '').split('/')[-1]
            patient = Patient.objects.get(patient_id=patient_id)

            episode = SepsisEpisode.objects.filter(patient=patient).order_by('-started_at').first()
            if not episode:
                return Response({"error": "No active episode."}, status=400)

            observed_at = parse_datetime(data.get('effectiveDateTime'))
            organism_name = data.get('valueCodeableConcept', {}).get('text', 'Unknown')
            organism = Organism.objects.filter(name=organism_name).order_by('-id').first()

            if not organism:
                return Response({"error": "Organism not found."}, status=400)

            antibiogram = Antibiogram.objects.create(
                organism=organism,
                created_at=observed_at
            )

            count = 0
            for comp in data.get('component', []):
                antibiotic = comp['code']['coding'][0]['display']
                result = comp.get('valueCodeableConcept', {}).get('text')

                if antibiotic and result:
                    AntibioticSusceptibility.objects.create(
                        antibiogram=antibiogram,
                        antibiotic=antibiotic,
                        result=result
                    )
                    count += 1

            if count == 0:
                return Response({"error": "No valid components."}, status=400)

            return Response({"status": f"{count} antibiogram entries recorded"}, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class FHIRVitalsIngestionView(APIView):
    def post(self, request):
        try:
            data = request.data
            patient_id = data.get('subject', {}).get('reference', '').split('/')[-1]
            patient = Patient.objects.get(patient_id=patient_id)

            episode = SepsisEpisode.objects.filter(patient=patient).order_by('-started_at').first()
            if not episode:
                return Response({"error": "No active episode."}, status=400)

            observed_at = parse_datetime(data.get('effectiveDateTime'))

            components = data.get('component', [])
            vitals = {}

            for comp in components:
                code = comp['code']['coding'][0]['code']
                value = comp.get('valueQuantity', {}).get('value')

                if value is None:
                    continue

                if code == '8480-6':
                    vitals['blood_pressure_sys'] = value
                elif code == '8462-4':
                    vitals['blood_pressure_dia'] = value
                elif code == '8867-4':
                    vitals['heart_rate'] = value
                elif code == '9279-1':
                    vitals['respiratory_rate'] = value
                elif code == '8310-5':
                    vitals['temperature'] = value
                elif code == '59408-5':
                    vitals['oxygen_saturation'] = value

            if not vitals:
                return Response({"error": "No valid vitals."}, status=400)

            VitalsObservation.objects.create(
                episode=episode,
                observed_at=observed_at,
                **vitals
            )

            return Response({"status": "vitals recorded"}, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class FHIRLabResultIngestionView(APIView):
    def post(self, request):
        try:
            data = request.data
            patient_id = data.get('subject', {}).get('reference', '').split('/')[-1]
            patient = Patient.objects.get(patient_id=patient_id)

            episode = SepsisEpisode.objects.filter(patient=patient).order_by('-started_at').first()
            if not episode:
                return Response({"error": "No active episode."}, status=400)

            observed_at = parse_datetime(data.get('effectiveDateTime'))

            LabResult.objects.create(
                episode=episode,
                exam_code=data['code']['coding'][0]['code'],
                exam_name=data['code']['coding'][0]['display'],
                value=data['valueQuantity']['value'],
                unit=data['valueQuantity'].get('unit'),
                observed_at=observed_at
            )

            return Response({"status": "lab result recorded"}, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class FHIRAntibioticAdministrationIngestionView(APIView):
    def post(self, request):
        try:
            data = request.data
            patient_id = data.get('subject', {}).get('reference', '').split('/')[-1]
            patient = Patient.objects.get(patient_id=patient_id)

            episode = SepsisEpisode.objects.filter(patient=patient).order_by('-started_at').first()
            if not episode:
                return Response({"error": "No active episode."}, status=400)

            AntibioticAdministration.objects.create(
                episode=episode,
                name=data.get('medicationCodeableConcept', {}).get('text'),
                started_at=parse_datetime(data.get('effectivePeriod', {}).get('start')),
                stopped_at=parse_datetime(data.get('effectivePeriod', {}).get('end')),
                dose=data.get('dosage', [{}])[0].get('text'),
                route=data.get('route', {}).get('text')
            )

            return Response({"status": "antibiotic administration recorded"}, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class FHIRClinicalNoteIngestionView(APIView):
    def post(self, request):
        try:
            data = request.data
            patient_id = data.get('subject', {}).get('reference', '').split('/')[-1]
            patient = Patient.objects.get(patient_id=patient_id)

            episode = SepsisEpisode.objects.filter(patient=patient).order_by('-started_at').first()
            if not episode:
                return Response({"error": "No active episode."}, status=400)

            ClinicalNote.objects.create(
                episode=episode,
                author=data.get('author', {}).get('display'),
                content=data.get('content', [{}])[0].get('text', {}).get('div'),
                created_at=parse_datetime(data.get('date'))
            )

            return Response({"status": "note recorded"}, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=400)
