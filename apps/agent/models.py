from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import JSONField

from apps.protocols.models import KnowledgeDocument

User = get_user_model()


class DocumentChunk(models.Model):
    document = models.ForeignKey(KnowledgeDocument, on_delete=models.CASCADE, related_name="chunks")
    chunk_index = models.PositiveIntegerField()
    text = models.TextField()

    processed = models.BooleanField(default=False)
    processing_attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("document", "chunk_index")
        ordering = ["document", "chunk_index"]

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"  


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)  # e.g. 'sepse', 'infection', 'oncology'
    document = models.ForeignKey(
        KnowledgeDocument,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Optional link to protocol document"
    )
    chunk = models.ForeignKey(
        DocumentChunk,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Chunk do qual essa tag foi extraída"
    )
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TagCondition(models.Model):
    tag = models.ForeignKey(Tag, related_name="conditions", on_delete=models.CASCADE)

    # one of: tag, field, event, natural_language
    condition_type = models.CharField(
        max_length=30,
        choices=[
            ("tag", "Tag"),
            ("field", "Field"),
            ("event", "Event"),
            ("natural_language", "Natural Language")
        ]
    )

    name = models.CharField(max_length=100)

    # for field conditions only
    field_path = models.CharField(max_length=255, blank=True, null=True)
    operator = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=[("<", "<"), (">", ">"), ("<=", "<="), (">=", ">="), ("==", "=="), ("!=", "!=")]
    )
    value = models.FloatField(blank=True, null=True)

    # for natural language conditions
    expression = models.TextField(blank=True, null=True, help_text="Free-text expression for complex or non-structured logic")

    def __str__(self):
        return f"{self.condition_type}:{self.name}"


class AgentExecutionLog(models.Model):
    agent_name = models.CharField(max_length=100)
    input_data = JSONField()
    output_data = JSONField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.agent_name}] at {self.created_at}"


class AgentExecutionEvent(models.Model):
    log = models.ForeignKey(AgentExecutionLog, on_delete=models.CASCADE, related_name="logs")
    message = models.TextField()
    metadata = JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
