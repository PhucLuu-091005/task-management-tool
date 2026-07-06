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

    # Manual status lifecycle. overdue is omitted as a target: it is system-managed by
    # flip_overdue_tasks and only ever cleared by moving to in_progress/done.
    ALLOWED_TRANSITIONS = {
        Status.NEW: {Status.IN_PROGRESS},
        Status.IN_PROGRESS: {Status.DONE},
        Status.DONE: set(),
        Status.OVERDUE: {Status.IN_PROGRESS, Status.DONE},
    }

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
    assigned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    @classmethod
    def can_transition(cls, from_status: str, to_status: str) -> bool:
        return to_status in cls.ALLOWED_TRANSITIONS.get(from_status, set())

    @property
    def is_overdue(self) -> bool:
        return bool(
            self.due_date and self.due_date < timezone.now() and self.status != self.Status.DONE
        )


TASK_LINK_URL_MAX_LENGTH = 500
TASK_LINK_LABEL_MAX_LENGTH = 200


class TaskStatusEvent(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="status_events")
    from_status = models.CharField(max_length=20, choices=Task.Status.choices)
    to_status = models.CharField(max_length=20, choices=Task.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="task_status_changes",
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["changed_at", "id"]

    def __str__(self) -> str:
        return f"Task {self.task_id}: {self.from_status} -> {self.to_status}"


class TaskLink(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="links")
    url = models.URLField(max_length=TASK_LINK_URL_MAX_LENGTH)
    label = models.CharField(max_length=TASK_LINK_LABEL_MAX_LENGTH, blank=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="task_links",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Link #{self.pk} on task {self.task_id}"


class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    image = models.ImageField(upload_to="task_attachments/%Y/%m/")
    caption = models.CharField(max_length=200, blank=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="task_attachments",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Attachment #{self.pk} on task {self.task_id}"
