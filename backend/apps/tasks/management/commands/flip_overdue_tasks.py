from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.tasks.models import Task


class Command(BaseCommand):
    help = "Flip past-due, unfinished tasks to the 'overdue' status."

    def handle(self, *args, **options):
        flipped = (
            Task.objects.filter(due_date__lt=timezone.now())
            .exclude(status__in=[Task.Status.DONE, Task.Status.OVERDUE])
            .update(status=Task.Status.OVERDUE)
        )
        self.stdout.write(self.style.SUCCESS(f"Flipped {flipped} task(s) to overdue."))
