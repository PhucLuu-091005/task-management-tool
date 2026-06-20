from django.conf import settings
from django.db import models
from django.utils import timezone


class Task(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"
        OVERDUE = "overdue", "Overdue"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class AssigneeType(models.TextChoices):
        USER = "user", "User"
        TEAM = "team", "Team"
        DEPARTMENT = "department", "Department"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    priority = models.CharField(max_length=10, choices=Priority.choices, blank=True, default="")

    assignee_type = models.CharField(max_length=20, choices=AssigneeType.choices)
    assignee_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
    )
    assignee_team = models.ForeignKey(
        "teams.Team",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
    )
    assignee_department = models.ForeignKey(
        "teams.Department",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_tasks",
    )
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    @property
    def is_overdue(self) -> bool:
        return bool(
            self.due_date and self.due_date < timezone.now() and self.status != self.Status.DONE
        )
