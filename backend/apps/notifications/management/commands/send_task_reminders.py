from django.core.management.base import BaseCommand

from apps.notifications.services import send_task_reminders


class Command(BaseCommand):
    help = "Email each assignee a digest of their due-today and overdue tasks."

    def handle(self, *args, **options):
        sent = send_task_reminders()
        self.stdout.write(self.style.SUCCESS(f"Sent {sent} reminder email(s)."))
