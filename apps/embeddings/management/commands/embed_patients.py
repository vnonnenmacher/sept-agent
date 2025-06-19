from django.core.management.base import BaseCommand
from apps.patients.models import Patient
from apps.embeddings.vector_pipeline import embed_and_store_patient


class Command(BaseCommand):
    help = 'Embed all patients into the vector DB'

    def handle(self, *args, **kwargs):
        patients = Patient.objects.all()

        for patient in patients:
            embed_and_store_patient(patient)

        self.stdout.write(self.style.SUCCESS('✅ All patients embedded successfully.'))
