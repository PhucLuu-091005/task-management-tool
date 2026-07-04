from django.db.models import Q
from rest_framework.permissions import SAFE_METHODS, BasePermission

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


def _leads_team(user, team_id):
    return TeamMembership.objects.filter(
        user=user, role=TeamMembership.Role.LEADER, team_id=team_id
    ).exists()


def _leads_team_in_department(user, department_id):
    return TeamMembership.objects.filter(
        user=user, role=TeamMembership.Role.LEADER, team__department_id=department_id
    ).exists()


def leader_can_assign(
    user, *, assignee_type, assignee_user_id, assignee_team_id, assignee_department_id
):
    """Whether a non-admin may target this assignee (README §5: leaders act within their group)."""
    if assignee_type == Task.AssigneeType.TEAM:
        return _leads_team(user, assignee_team_id)
    if assignee_type == Task.AssigneeType.DEPARTMENT:
        return _leads_team_in_department(user, assignee_department_id)
    if assignee_type == Task.AssigneeType.USER:
        led_team_ids = TeamMembership.objects.filter(
            user=user, role=TeamMembership.Role.LEADER
        ).values_list("team_id", flat=True)
        return TeamMembership.objects.filter(
            team_id__in=led_team_ids, user_id=assignee_user_id
        ).exists()
    return False


class CanCreateTask(BasePermission):
    """README §5: only admins and team leaders may create/assign tasks; anyone may still read."""

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        if getattr(user, "is_admin", False):
            return True
        return TeamMembership.objects.filter(user=user, role=TeamMembership.Role.LEADER).exists()


class CanEditTask(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        # Reads are already scoped by get_queryset=visible_tasks; only writes need the gate below,
        # so a member who can see a task in the list can still retrieve its detail.
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if getattr(user, "is_admin", False) or obj.created_by_id == user.id:
            return True
        if obj.assignee_team_id and _leads_team(user, obj.assignee_team_id):
            return True
        if obj.assignee_department_id:
            return _leads_team_in_department(user, obj.assignee_department_id)
        return False
