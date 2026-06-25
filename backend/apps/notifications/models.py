from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Kind(models.TextChoices):
        TASK_ASSIGNED = "task_assigned", "Task assigned"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    kind = models.CharField(max_length=32, choices=Kind.choices, default=Kind.TASK_ASSIGNED)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.kind} -> {self.recipient} (task {self.task_id})"
