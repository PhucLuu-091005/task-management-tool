from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.users.bootstrap import seed_admin_from_env


class Command(BaseCommand):
    help = (
        "Create or promote an app admin from INITIAL_ADMIN_* env vars (idempotent). "
        "Safe to run on every deploy; a no-op when the vars are unset."
    )

    def handle(self, *args, **options):
        user = seed_admin_from_env(get_user_model())
        if user is None:
            self.stdout.write(
                "Skipped: INITIAL_ADMIN_USERNAME/INITIAL_ADMIN_PASSWORD not set."
            )
            return
        self.stdout.write(self.style.SUCCESS(f"Ensured admin '{user.username}'."))
