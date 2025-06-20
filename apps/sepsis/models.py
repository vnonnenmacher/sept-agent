from django.db import models
from apps.patients.models import Patient


class SepsisEpisode(models.Model):
    """
    A single instance of a patient undergoing the sepsis protocol.
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='sepsis_episodes')
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Sepsis episode for {self.patient} starting {self.started_at}"


# 🔬 Sample and Microbiology

class Sample(models.Model):
    """
    Biological material collected for culture (e.g., blood, urine).
    """
    episode = models.ForeignKey(SepsisEpisode, on_delete=models.CASCADE, related_name='samples')
    material = models.CharField(max_length=100)  # e.g., "Blood", "Urine"
    collected_at = models.DateTimeField()

    def __str__(self):
        return f"Sample {self.material} collected at {self.collected_at}"


class CultureResult(models.Model):
    """
    Result of a culture from a sample.
    """
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='culture_results')
    result = models.CharField(
        max_length=20,
        choices=[('positive', 'Positive'), ('negative', 'Negative')],
    )
    reported_at = models.DateTimeField()

    def __str__(self):
        return f"Culture {self.result} for {self.sample}"


class Organism(models.Model):
    """
    Organism found in a positive culture.
    """
    culture_result = models.ForeignKey(CultureResult, on_delete=models.CASCADE, related_name='organisms')
    name = models.CharField(max_length=100)  # e.g., "Escherichia coli"

    def __str__(self):
        return f"{self.name} in {self.culture_result}"


class Antibiogram(models.Model):
    """
    Antibiogram for a given organism within a culture.
    """
    organism = models.ForeignKey(Organism, on_delete=models.CASCADE, related_name='antibiograms')
    created_at = models.DateTimeField()

    def __str__(self):
        return f"Antibiogram for {self.organism}"


class AntibioticSusceptibility(models.Model):
    """
    Single line in an antibiogram: antibiotic + result (S/I/R).
    """
    antibiogram = models.ForeignKey(Antibiogram, on_delete=models.CASCADE, related_name='susceptibilities')
    antibiotic = models.CharField(max_length=100)
    result = models.CharField(
        max_length=20,
        choices=[
            ('S', 'Susceptible'),
            ('I', 'Intermediate'),
            ('R', 'Resistant'),
        ],
    )

    def __str__(self):
        return f"{self.antibiotic}: {self.result} ({self.antibiogram})"


# 💉 Antibiotic Management

class AntibioticAdministration(models.Model):
    """
    Antibiotic given to the patient during the sepsis episode.
    """
    episode = models.ForeignKey(SepsisEpisode, on_delete=models.CASCADE, related_name='antibiotics')
    name = models.CharField(max_length=100)
    started_at = models.DateTimeField()
    stopped_at = models.DateTimeField(null=True, blank=True)
    dose = models.CharField(max_length=100, null=True, blank=True)  # Optional
    route = models.CharField(max_length=50, null=True, blank=True)  # e.g., IV, oral

    def __str__(self):
        return f"{self.name} for {self.episode}"


# 🧪 Non-Micro Labs

class LabResult(models.Model):
    """
    Non-microbiological lab result (e.g., creatinine, CRP).
    """
    episode = models.ForeignKey(SepsisEpisode, on_delete=models.CASCADE, related_name='lab_results')
    exam_code = models.CharField(max_length=50)    # Optional coding
    exam_name = models.CharField(max_length=255)
    value = models.FloatField()
    unit = models.CharField(max_length=50, null=True, blank=True)
    observed_at = models.DateTimeField()

    def __str__(self):
        return f"{self.exam_name}: {self.value} {self.unit} at {self.observed_at}"


# ❤️ Vitals

class VitalsObservation(models.Model):
    """
    Vitals for the patient during the episode.
    """
    episode = models.ForeignKey(SepsisEpisode, on_delete=models.CASCADE, related_name='vitals')
    observed_at = models.DateTimeField()

    heart_rate = models.IntegerField(null=True, blank=True)               # BPM
    respiratory_rate = models.IntegerField(null=True, blank=True)         # RPM
    temperature = models.FloatField(null=True, blank=True)                # Celsius
    blood_pressure_sys = models.IntegerField(null=True, blank=True)       # mmHg
    blood_pressure_dia = models.IntegerField(null=True, blank=True)       # mmHg
    oxygen_saturation = models.IntegerField(null=True, blank=True)        # %

    def __str__(self):
        return f"Vitals at {self.observed_at}"


# 🗒️ Clinical Notes

class ClinicalNote(models.Model):
    """
    Free-text note from clinicians during the episode.
    """
    episode = models.ForeignKey(SepsisEpisode, on_delete=models.CASCADE, related_name='notes')
    author = models.CharField(max_length=100, null=True, blank=True)  # Optional: who wrote it
    content = models.TextField()
    created_at = models.DateTimeField()

    def __str__(self):
        return f"Note at {self.created_at}: {self.content[:30]}..."
