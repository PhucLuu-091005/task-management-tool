"""RBAC permissions. Single-responsibility and composable: admin's "access all"
is expressed per-view via ``IsAdmin | IsTeamLeader``, not baked into each class.

The team-scoped classes decide at the object level; view-level they only check
authentication, so a consumer must filter the queryset (list) and add an explicit
guard such as ``IsAdmin`` for create — these classes don't secure those alone."""

from rest_framework.permissions import BasePermission

from apps.teams.models import Team, TeamMembership


def _resolve_team(obj) -> Team | None:
    if isinstance(obj, Team):
        return obj
    return getattr(obj, "team", None)


class IsAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.is_admin)

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)


class CanListUsers(BasePermission):
    """Admins and anyone who can assign tasks (team leaders, department leads) may
    list users; the view's queryset then scopes non-admins to the people they can
    actually assign. A plain member has no one to assign, so they're denied here."""

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user and user.is_authenticated and getattr(user, "can_create_tasks", False)
        )


class IsTeamLeader(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        team = _resolve_team(obj)
        if team is None:
            return False
        return TeamMembership.objects.filter(
            user=request.user, team=team, role=TeamMembership.Role.LEADER
        ).exists()


class IsTeamMember(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        team = _resolve_team(obj)
        if team is None:
            return False
        return TeamMembership.objects.filter(user=request.user, team=team).exists()
