# apps/sepsis/serializers.py

from rest_framework import serializers
from apps.patients.models import Patient
from .models import (
    SepsisEpisode, Sample, CultureResult, Organism, Antibiogram,
    AntibioticSusceptibility, AntibioticAdministration, LabResult,
    VitalsObservation, ClinicalNote
)


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['patient_id', 'name', 'birth_date', 'gender']


# 🔬 Microbiology serializers

class AntibioticSusceptibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AntibioticSusceptibility
        fields = ['antibiotic', 'result']


class AntibiogramSerializer(serializers.ModelSerializer):
    susceptibilities = AntibioticSusceptibilitySerializer(many=True, read_only=True)

    class Meta:
        model = Antibiogram
        fields = ['id', 'created_at', 'susceptibilities']


class OrganismSerializer(serializers.ModelSerializer):
    antibiograms = AntibiogramSerializer(many=True, read_only=True)

    class Meta:
        model = Organism
        fields = ['id', 'name', 'antibiograms']


class CultureResultSerializer(serializers.ModelSerializer):
    organisms = OrganismSerializer(many=True, read_only=True)

    class Meta:
        model = CultureResult
        fields = ['id', 'result', 'reported_at', 'organisms']


class SampleSerializer(serializers.ModelSerializer):
    culture_results = CultureResultSerializer(many=True, read_only=True)

    class Meta:
        model = Sample
        fields = ['id', 'material', 'collected_at', 'culture_results']


# 💉 Antibiotics

class AntibioticAdministrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntibioticAdministration
        fields = ['id', 'name', 'started_at', 'stopped_at', 'dose', 'route']


# 🧪 Labs

class LabResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabResult
        fields = ['id', 'exam_code', 'exam_name', 'value', 'unit', 'observed_at']


# ❤️ Vitals

class VitalsObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalsObservation
        fields = [
            'id', 'observed_at', 'heart_rate', 'respiratory_rate', 'temperature',
            'blood_pressure_sys', 'blood_pressure_dia', 'oxygen_saturation'
        ]


# 🗒️ Notes

class ClinicalNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalNote
        fields = ['id', 'author', 'content', 'created_at']


# 🩸 🔥 Main Episode Serializer

class SepsisEpisodeDetailSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    samples = SampleSerializer(many=True, read_only=True)
    antibiotics = AntibioticAdministrationSerializer(many=True, read_only=True)
    lab_results = LabResultSerializer(many=True, read_only=True)
    vitals = VitalsObservationSerializer(many=True, read_only=True)
    notes = ClinicalNoteSerializer(many=True, read_only=True)

    class Meta:
        model = SepsisEpisode
        fields = [
            'id', 'patient', 'started_at', 'ended_at',
            'samples', 'antibiotics', 'lab_results',
            'vitals', 'notes'
        ]

class SepsisEpisodeListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = SepsisEpisode
        fields = ['id', 'patient_id', 'patient_name', 'started_at', 'ended_at', 'status']

    def get_status(self, obj):
        return 'open' if obj.ended_at is None else 'closed'
