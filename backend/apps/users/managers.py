from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.db.models import Prefetch

from apps.teams.models import TeamMembership

# Single source of truth for the memberships+team prefetch shape. Reused by
# UserQuerySet.with_memberships (lookup paths) and by views that already hold
# a User instance via prefetch_related_objects (e.g. ProfileView).
MEMBERSHIPS_PREFETCH = Prefetch(
    "memberships", queryset=TeamMembership.objects.select_related("team")
)


class UserQuerySet(models.QuerySet):
    def with_memberships(self):
        return self.prefetch_related(MEMBERSHIPS_PREFETCH)


# Inherit from DjangoUserManager to keep create_user/create_superuser, and use
# from_queryset to expose the chainable UserQuerySet methods on the manager.
class UserManager(DjangoUserManager.from_queryset(UserQuerySet)):
    pass
