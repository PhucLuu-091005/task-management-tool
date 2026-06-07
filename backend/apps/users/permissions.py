"""RBAC permissions. Single-responsibility and composable: admin's "access all"
is expressed per-view via ``IsAdmin | IsTeamLeader``, not baked into each class."""

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
