from django.contrib.auth.models import AbstractUser
from django.db import models

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
