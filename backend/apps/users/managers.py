from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.db.models import Prefetch, Q

from apps.teams.models import Team, TeamMembership

# Single source of truth for the memberships+team prefetch shape. Reused by
# UserQuerySet.with_memberships (lookup paths) and by views that already hold
# a User instance via prefetch_related_objects (e.g. ProfileView).
MEMBERSHIPS_PREFETCH = Prefetch(
    "memberships", queryset=TeamMembership.objects.select_related("team")
)

# Everything UserSerializer touches: memberships (roles) plus led_departments, so
# `can_create_tasks` resolves without a per-user query on the profile / user list.
PROFILE_PREFETCHES = (MEMBERSHIPS_PREFETCH, "led_departments")


class UserQuerySet(models.QuerySet):
    def with_memberships(self):
        return self.prefetch_related(*PROFILE_PREFETCHES)

    def assignable_by(self, user):
        """Users `user` may see as task assignees (README §5). Admins see everyone;
        a lead sees the people they manage — members of teams they lead or of teams
        in departments they lead — plus themselves, so self-assignment still works.
        Kept in sync with tasks.permissions.can_manage_assignee."""
        qs = self.with_memberships()
        if getattr(user, "is_admin", False):
            return qs
        led_team_ids = TeamMembership.objects.filter(
            user=user, role=TeamMembership.Role.LEADER
        ).values_list("team_id", flat=True)
        dept_team_ids = Team.objects.filter(department__lead=user).values_list("id", flat=True)
        managed_team_ids = set(led_team_ids) | set(dept_team_ids)
        return qs.filter(Q(pk=user.pk) | Q(memberships__team_id__in=managed_team_ids)).distinct()


# Inherit from DjangoUserManager to keep create_user/create_superuser, and use
# from_queryset to expose the chainable UserQuerySet methods on the manager.
class UserManager(DjangoUserManager.from_queryset(UserQuerySet)):
    pass
