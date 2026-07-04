from django.db.models import Q
from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.tasks.models import Task
from apps.teams.models import Department, TeamMembership


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
        # a department lead sees (and so can open/edit) their department's tasks
        | Q(assignee_department__lead=user)
    ).distinct()


def _leads_team(user, team_id):
    return (
        bool(team_id)
        and TeamMembership.objects.filter(
            user=user, role=TeamMembership.Role.LEADER, team_id=team_id
        ).exists()
    )


def _leads_target_users_team(user, target_user_id):
    if not target_user_id:
        return False
    led_team_ids = TeamMembership.objects.filter(
        user=user, role=TeamMembership.Role.LEADER
    ).values_list("team_id", flat=True)
    return TeamMembership.objects.filter(team_id__in=led_team_ids, user_id=target_user_id).exists()


def _leads_department(user, department_id):
    return bool(department_id) and Department.objects.filter(id=department_id, lead=user).exists()


def _is_any_leader(user):
    return (
        TeamMembership.objects.filter(user=user, role=TeamMembership.Role.LEADER).exists()
        or Department.objects.filter(lead=user).exists()
    )


def can_manage_assignee(
    user, *, assignee_type, assignee_user_id, assignee_team_id, assignee_department_id
):
    """Non-admin authority over a task's assignee (README §5): a team leader manages their own team
    and its members; a department lead manages department-scoped tasks. Nobody else."""
    if assignee_type == Task.AssigneeType.TEAM:
        return _leads_team(user, assignee_team_id)
    if assignee_type == Task.AssigneeType.USER:
        return _leads_target_users_team(user, assignee_user_id)
    if assignee_type == Task.AssigneeType.DEPARTMENT:
        return _leads_department(user, assignee_department_id)
    return False


class CanCreateTask(BasePermission):
    """README §5: only admins, team leaders and dept leads may create/assign; anyone may read."""

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return getattr(user, "is_admin", False) or _is_any_leader(user)


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
        return can_manage_assignee(
            user,
            assignee_type=obj.assignee_type,
            assignee_user_id=obj.assignee_user_id,
            assignee_team_id=obj.assignee_team_id,
            assignee_department_id=obj.assignee_department_id,
        )
