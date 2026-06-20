from rest_framework import serializers

from apps.tasks.constants import (
    ASSIGNEE_MISMATCH_ERROR_MESSAGE,
    ASSIGNEE_REQUIRED_ERROR_MESSAGE,
)
from apps.tasks.models import Task

_ASSIGNEE_FIELDS = {
    Task.AssigneeType.USER: "assignee_user",
    Task.AssigneeType.TEAM: "assignee_team",
    Task.AssigneeType.DEPARTMENT: "assignee_department",
}


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
            "assignee_type",
            "assignee_user",
            "assignee_team",
            "assignee_department",
            "created_by",
            "due_date",
            "is_overdue",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "created_by", "created_at", "updated_at"]

    def validate(self, data: dict) -> dict:
        assignee_type = data.get("assignee_type")
        expected_field = _ASSIGNEE_FIELDS[assignee_type]
        for field in _ASSIGNEE_FIELDS.values():
            value = data.get(field)
            if field == expected_field and value is None:
                raise serializers.ValidationError(
                    {field: ASSIGNEE_REQUIRED_ERROR_MESSAGE.format(type=assignee_type)}
                )
            if field != expected_field and value is not None:
                raise serializers.ValidationError(
                    {field: ASSIGNEE_MISMATCH_ERROR_MESSAGE.format(type=assignee_type)}
                )
        return data
