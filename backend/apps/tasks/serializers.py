from rest_framework import serializers

from apps.tasks.constants import NOT_TEAM_MEMBER_ERROR_MESSAGE
from apps.tasks.models import Task
from apps.teams.models import Team, TeamMembership


class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "estimate_hours",
            "assignee",
            "created_by",
            "team",
            "due_date",
            "is_overdue",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "assignee",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def validate_team(self, value: Team) -> Team:
        user = self.context["request"].user
        if user.is_admin:
            return value
        if not TeamMembership.objects.filter(user=user, team=value).exists():
            raise serializers.ValidationError(NOT_TEAM_MEMBER_ERROR_MESSAGE)
        return value
