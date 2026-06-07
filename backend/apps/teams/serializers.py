from django.db import IntegrityError
from rest_framework import serializers

from apps.teams.constants import ALREADY_MEMBER_ERROR_MESSAGE
from apps.teams.models import Team, TeamMembership


class TeamMembershipSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)

    class Meta:
        model = TeamMembership
        fields = ["team", "team_name", "role"]


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMembership
        fields = ["user", "role"]

    def validate(self, attrs: dict) -> dict:
        if TeamMembership.objects.filter(user=attrs["user"], team=self.context["team"]).exists():
            raise serializers.ValidationError({"user": ALREADY_MEMBER_ERROR_MESSAGE})
        return attrs

    def create(self, validated_data: dict) -> TeamMembership:
        # validate() catches the sequential case; the unique (user, team) constraint
        # is the real guard against the concurrent check-then-insert race (else 500).
        try:
            return super().create(validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError({"user": ALREADY_MEMBER_ERROR_MESSAGE}) from exc


class TeamMemberRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMembership
        fields = ["user", "role"]
        read_only_fields = ["user"]
