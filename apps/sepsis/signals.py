from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from apps.patients.models import Patient
from apps.sepsis.models import (
    SepsisEpisode,
    CultureResult,
    Organism,
    VitalsObservation,
    LabResult,
    Antibiogram,
    AntibioticAdministration,
    ClinicalNote
)

from apps.embeddings.tasks import (
    embed_patient_task,
    embed_episode_task,
    embed_culture_task,
    embed_organism_task,
    embed_vitals_task,
    embed_lab_task,
    embed_antibiogram_task,
    embed_antibiotic_task,
    embed_clinical_note_task
)


@receiver(post_save, sender=Patient)
def patient_created_handler(sender, instance, created, **kwargs):
    if created:
        print(f"🚀 Trigger embedding for Patient {instance.patient_id}")
        transaction.on_commit(lambda: embed_patient_task.delay(instance.patient_id))


@receiver(post_save, sender=SepsisEpisode)
def episode_created_handler(sender, instance, created, **kwargs):
    if created:
        print(f"🚀 Trigger embedding for Episode {instance.id}")
        transaction.on_commit(lambda: embed_episode_task.delay(instance.id))


@receiver(post_save, sender=CultureResult)
def culture_created_handler(sender, instance, created, **kwargs):
    if created:
        print(f"🚀 Trigger embedding for Culture {instance.id}")
        transaction.on_commit(lambda: embed_culture_task.delay(instance.id))


@receiver(post_save, sender=Organism)
def organism_created_handler(sender, instance, created, **kwargs):
    if created:
        print(f"🚀 Trigger embedding for Organism {instance.id}")
        transaction.on_commit(lambda: embed_organism_task.delay(instance.id))


@receiver(post_save, sender=VitalsObservation)
def vitals_created_handler(sender, instance, created, **kwargs):
    if created:
        print(f"🚀 Trigger embedding for Vitals {instance.id}")
        transaction.on_commit(lambda: embed_vitals_task.delay(instance.id))


@receiver(post_save, sender=LabResult)
def lab_created_handler(sender, instance, created, **kwargs):
    if created:
        print(f"🚀 Trigger embedding for Lab {instance.id}")
        transaction.on_commit(lambda: embed_lab_task.delay(instance.id))


@receiver(post_save, sender=Antibiogram)
def antibiogram_created_handler(sender, instance, created, **kwargs):
    if created:
        print(f"🚀 Trigger embedding for Antibiogram {instance.id}")
        transaction.on_commit(lambda: embed_antibiogram_task.delay(instance.id))


@receiver(post_save, sender=AntibioticAdministration)
def antibiotic_created_handler(sender, instance, created, **kwargs):
    if created:
        print(f"🚀 Trigger embedding for Antibiotic {instance.id}")
        transaction.on_commit(lambda: embed_antibiotic_task.delay(instance.id))


@receiver(post_save, sender=ClinicalNote)
def note_created_handler(sender, instance, created, **kwargs):
    if created:
        print(f"🚀 Trigger embedding for Clinical Note {instance.id}")
        transaction.on_commit(lambda: embed_clinical_note_task.delay(instance.id))
