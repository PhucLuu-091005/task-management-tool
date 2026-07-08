from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.teams.models import TeamMembership
from apps.users.managers import UserManager


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    teams = models.ManyToManyField(
        "teams.Team", through="teams.TeamMembership", related_name="members"
    )
    is_admin = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="avatars/%Y/%m/", null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self) -> str:
        return self.email

    @property
    def can_create_tasks(self) -> bool:
        # Single source of truth for tasks.CanCreateTask and the profile API:
        # admins, team leaders, and department leads may create/assign tasks.
        # Reads prefetched `memberships`/`led_departments` when present (no query),
        # so it's flat on the profile and admin user-list serializers.
        if self.is_admin:
            return True
        if any(m.role == TeamMembership.Role.LEADER for m in self.memberships.all()):
            return True
        return bool(self.led_departments.all())
