from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from apps.patients.models import Patient
from apps.sepsis.models import (
    VitalsObservation,
    LabResult,
    Antibiogram,
    AntibioticAdministration,
    ClinicalNote
)

from apps.embeddings.tasks import (
    embed_patient_task,
    embed_vitals_task,
    embed_lab_task,
    embed_antibiogram_task,
    embed_antibiotic_task,
    embed_clinical_note_task
)


@receiver(post_save, sender=Patient)
def patient_created_handler(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: embed_patient_task.delay(instance.patient_id))


@receiver(post_save, sender=VitalsObservation)
def vitals_created_handler(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: embed_vitals_task.delay(instance.id))


@receiver(post_save, sender=LabResult)
def lab_created_handler(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: embed_lab_task.delay(instance.id))


@receiver(post_save, sender=Antibiogram)
def antibiogram_created_handler(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: embed_antibiogram_task.delay(instance.id))


@receiver(post_save, sender=AntibioticAdministration)
def antibiotic_created_handler(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: embed_antibiotic_task.delay(instance.id))


@receiver(post_save, sender=ClinicalNote)
def note_created_handler(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: embed_clinical_note_task.delay(instance.id))
