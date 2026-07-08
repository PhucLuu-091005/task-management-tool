from django.db.models import Q
from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.tasks.models import Task
from apps.teams.models import Department, Team, TeamMembership


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
        # a department lead oversees their whole department: its own tasks, its teams'
        # tasks, and tasks for members of those teams.
        | Q(assignee_department__lead=user)
        | Q(assignee_team__department__lead=user)
        | Q(assignee_user__memberships__team__department__lead=user)
    ).distinct()


def _manages_team(user, team_id):
    """user has authority over a team: they lead it, or they lead its department."""
    if not team_id:
        return False
    if TeamMembership.objects.filter(
        user=user, role=TeamMembership.Role.LEADER, team_id=team_id
    ).exists():
        return True
    return Team.objects.filter(id=team_id, department__lead=user).exists()


def _manages_target_user(user, target_user_id):
    """target user belongs to a team `user` manages (as team leader or department lead)."""
    if not target_user_id:
        return False
    target_team_ids = list(
        TeamMembership.objects.filter(user_id=target_user_id).values_list("team_id", flat=True)
    )
    if not target_team_ids:
        return False
    leads_a_team = TeamMembership.objects.filter(
        user=user, role=TeamMembership.Role.LEADER, team_id__in=target_team_ids
    ).exists()
    leads_their_department = Team.objects.filter(
        id__in=target_team_ids, department__lead=user
    ).exists()
    return leads_a_team or leads_their_department


def _leads_department(user, department_id):
    return bool(department_id) and Department.objects.filter(id=department_id, lead=user).exists()


def can_manage_assignee(
    user, *, assignee_type, assignee_user_id, assignee_team_id, assignee_department_id
):
    """Non-admin authority over a task's assignee (README §5). A team leader manages their own team
    and its members; a department lead outranks that and manages the whole department — its teams,
    their members, and department-scoped tasks. Nobody else."""
    if assignee_type == Task.AssigneeType.TEAM:
        return _manages_team(user, assignee_team_id)
    if assignee_type == Task.AssigneeType.USER:
        return _manages_target_user(user, assignee_user_id)
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
        return bool(getattr(user, "can_create_tasks", False))


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


class CanDeleteTaskItem(BasePermission):
    """Task sub-items (attachments, links): deletable by whoever added them or a task editor."""

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not (user and user.is_authenticated):
            return False
        # Guard against a SET_NULL'd uploader: None == None must not grant delete.
        if obj.added_by_id is not None and obj.added_by_id == user.id:
            return True
        return CanEditTask().has_object_permission(request, view, obj.task)
