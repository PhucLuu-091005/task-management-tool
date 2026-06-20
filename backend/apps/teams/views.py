from functools import cached_property

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics

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
