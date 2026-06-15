from django.db.models import QuerySet
from rest_framework.permissions import BasePermission

from apps.tasks.models import Task
from apps.teams.models import TeamMembership


def visible_tasks(user) -> QuerySet[Task]:
    if not (user and user.is_authenticated):
        return Task.objects.none()
    if user.is_admin:
        return Task.objects.all()
    return Task.objects.filter(team__memberships__user=user).distinct()


class IsTaskTeamMember(BasePermission):
    # Auth-only guard; team membership on create is enforced in TaskSerializer.validate_team.
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated)


class CanEditTask(BasePermission):
    def has_object_permission(self, request, view, obj: Task) -> bool:
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if user.is_admin or obj.created_by_id == user.id:
            return True
        return TeamMembership.objects.filter(
            user=user, team=obj.team, role=TeamMembership.Role.LEADER
        ).exists()
