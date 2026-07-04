from django.db.models import Q
from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.tasks.models import Task
from apps.teams.models import TeamMembership


def _user_team_ids(user):
    return list(TeamMembership.objects.filter(user=user).values_list("team_id", flat=True))


def visible_tasks(user):
    qs = Task.objects.select_related(
        "assignee_user", "assignee_team", "assignee_department", "created_by"
    )
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


class CanEditTaskOrReadOnly(CanEditTask):
    """Anyone who can see the task (queryset-scoped) may read it; edits stay gated."""

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return super().has_object_permission(request, view, obj)


class CanDeleteTaskItem(BasePermission):
    """Task sub-items (attachments, links): deletable by whoever added them or a task editor."""

    def has_object_permission(self, request, view, obj) -> bool:
        if obj.added_by_id == request.user.id:
            return True
        return CanEditTask().has_object_permission(request, view, obj.task)
