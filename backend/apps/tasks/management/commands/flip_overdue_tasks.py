from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.tasks.models import Task, TaskStatusEvent


class Command(BaseCommand):
    help = "Flip past-due, unfinished tasks to the 'overdue' status."

    def handle(self, *args, **options):
        due = Task.objects.filter(due_date__lt=timezone.now()).exclude(
            status__in=[Task.Status.DONE, Task.Status.OVERDUE]
        )
        # Snapshot each task's current status before the bulk update so the history
        # rows carry the real from_status; changed_by is None for this system flip.
        snapshot = list(due.values_list("id", "status"))
        with transaction.atomic():
            due.update(status=Task.Status.OVERDUE)
            TaskStatusEvent.objects.bulk_create(
                TaskStatusEvent(
                    task_id=task_id,
                    from_status=from_status,
                    to_status=Task.Status.OVERDUE,
                    changed_by=None,
                )
                for task_id, from_status in snapshot
            )
        self.stdout.write(self.style.SUCCESS(f"Flipped {len(snapshot)} task(s) to overdue."))
