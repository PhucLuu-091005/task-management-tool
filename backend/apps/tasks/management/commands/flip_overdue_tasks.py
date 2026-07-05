from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.tasks.models import Task, TaskStatusEvent


class Command(BaseCommand):
    help = "Flip past-due, unfinished tasks to the 'overdue' status."

    def handle(self, *args, **options):
        with transaction.atomic():
            due = (
                Task.objects.select_for_update()
                .filter(due_date__lt=timezone.now())
                .exclude(status__in=[Task.Status.DONE, Task.Status.OVERDUE])
            )
            # Lock and snapshot the eligible rows so the flip and its history rows
            # describe exactly the same set even under a concurrent status write;
            # changed_by is None for this system flip.
            snapshot = list(due.values_list("id", "status"))
            ids = [task_id for task_id, _ in snapshot]
            Task.objects.filter(id__in=ids).update(status=Task.Status.OVERDUE)
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
