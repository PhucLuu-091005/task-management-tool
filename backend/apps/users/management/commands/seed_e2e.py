import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

# Defaults mirror frontend/e2e/admin.ts; override via env for CI or shared envs.
DEFAULT_USERNAME = "e2eadmin"
DEFAULT_PASSWORD = "Passw0rd!e2e"
DEFAULT_EMAIL = "e2eadmin@example.com"
DEFAULT_LAST_NAME = "E2E"
DEFAULT_FIRST_NAME = "Admin"


class Command(BaseCommand):
    help = "Ensure a known admin account exists for E2E tests (idempotent)."

    def handle(self, *args, **options):
        # This grants a known-credential admin; refuse outside dev so a stray run
        # can't provision a backdoor account in production.
        if not settings.DEBUG and os.environ.get("E2E_SEED_ALLOWED") != "1":
            raise CommandError(
                "seed_e2e refuses to run with DEBUG=False; set E2E_SEED_ALLOWED=1 to override."
            )

        User = get_user_model()
        username = os.environ.get("E2E_ADMIN_USERNAME", DEFAULT_USERNAME)
        password = os.environ.get("E2E_ADMIN_PASSWORD", DEFAULT_PASSWORD)
        email = os.environ.get("E2E_ADMIN_EMAIL", DEFAULT_EMAIL)

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "last_name": DEFAULT_LAST_NAME,
                "first_name": DEFAULT_FIRST_NAME,
            },
        )
        # Reset each run so a locally-mutated account can't fail the suite.
        user.email = email
        user.is_admin = True
        user.is_active = True
        user.set_password(password)
        user.save()

        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{verb} E2E admin '{username}'."))
