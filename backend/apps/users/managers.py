from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.db.models import Prefetch

from apps.teams.models import TeamMembership


class UserQuerySet(models.QuerySet):
    def with_memberships(self):
        # Prefetch memberships + their teams so serializing team names is N+1-free.
        return self.prefetch_related(
            Prefetch("memberships", queryset=TeamMembership.objects.select_related("team"))
        )


# Inherit from DjangoUserManager to keep create_user/create_superuser, and use
# from_queryset to expose the chainable UserQuerySet methods on the manager.
class UserManager(DjangoUserManager.from_queryset(UserQuerySet)):
    pass
