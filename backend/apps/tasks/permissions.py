from django.db.models import Q
from rest_framework.permissions import BasePermission

from apps.tasks.models import Task
from apps.teams.models import TeamMembership


def _user_team_ids(user):
    return list(TeamMembership.objects.filter(user=user).values_list("team_id", flat=True))


def visible_tasks(user):
    qs = Task.objects.all()
    if getattr(user, "is_admin", False):
        return qs
    team_ids = _user_team_ids(user)
    return qs.filter(
        Q(created_by=user)
        | Q(assignee_user=user)
        | Q(assignee_team_id__in=team_ids)
        | Q(assignee_department__teams__id__in=team_ids)
    ).distinct()


class CanEditTask(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if getattr(user, "is_admin", False) or obj.created_by_id == user.id:
            return True
        leader_team_ids = TeamMembership.objects.filter(
            user=user, role=TeamMembership.Role.LEADER
        ).values_list("team_id", flat=True)
        if obj.assignee_team_id and obj.assignee_team_id in leader_team_ids:
            return True
        if obj.assignee_department_id:
            return obj.assignee_department.teams.filter(id__in=leader_team_ids).exists()
        return False
