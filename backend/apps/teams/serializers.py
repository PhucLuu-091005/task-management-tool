from rest_framework import serializers

from apps.teams.models import TeamMembership


class TeamMembershipSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source="team.name", read_only=True)

    class Meta:
        model = TeamMembership
        fields = ["team", "team_name", "role"]
