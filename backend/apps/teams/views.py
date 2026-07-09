from functools import cached_property

from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response

from apps.tasks.models import Task
from apps.teams.constants import (
    DEPARTMENT_ASSIGNED_TASKS_ERROR_MESSAGE,
    DEPARTMENT_HAS_TEAMS_ERROR_MESSAGE,
    TEAM_ASSIGNED_TASKS_ERROR_MESSAGE,
)
from apps.teams.models import Department, Team, TeamMembership
from apps.teams.serializers import (
    DepartmentSerializer,
    TeamMemberRoleSerializer,
    TeamMemberSerializer,
    TeamSerializer,
)
from apps.users.permissions import IsAdmin


class TeamListCreateView(generics.ListCreateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        with transaction.atomic():
            team = serializer.save()
            TeamMembership.objects.create(
                user=self.request.user, team=team, role=TeamMembership.Role.LEADER
            )


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAdmin]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # assignee_team is SET_NULL, so deleting a team with tasks assigned to it
        # would leave them in an invalid "type=team, assignee=null" state; block it.
        if Task.objects.filter(assignee_team=instance).exists():
            return Response(
                {"detail": TEAM_ASSIGNED_TASKS_ERROR_MESSAGE},
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)


class TeamMemberCreateView(generics.CreateAPIView):
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAdmin]

    @cached_property
    def team(self) -> Team:
        return get_object_or_404(Team, pk=self.kwargs["team_id"])

    def get_serializer_context(self) -> dict:
        return {**super().get_serializer_context(), "team": self.team}

    def perform_create(self, serializer):
        serializer.save(team=self.team)


class TeamMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeamMemberRoleSerializer
    permission_classes = [IsAdmin]

    def get_object(self) -> TeamMembership:
        membership = get_object_or_404(
            TeamMembership, team_id=self.kwargs["team_id"], user_id=self.kwargs["user_id"]
        )
        self.check_object_permissions(self.request, membership)
        return membership


class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdmin]


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdmin]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # assignee_department is SET_NULL, so deleting a department with tasks
        # assigned to it would leave them in an invalid "type=department,
        # assignee=null" state; block it.
        if Task.objects.filter(assignee_department=instance).exists():
            return Response(
                {"detail": DEPARTMENT_ASSIGNED_TASKS_ERROR_MESSAGE},
                status=status.HTTP_409_CONFLICT,
            )
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            # Team.department is PROTECT, so a department that still owns teams
            # can't be removed; report it cleanly instead of a raw 500.
            return Response(
                {"detail": DEPARTMENT_HAS_TEAMS_ERROR_MESSAGE},
                status=status.HTTP_409_CONFLICT,
            )
