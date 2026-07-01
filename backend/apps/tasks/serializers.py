from rest_framework import serializers

from apps.tasks.constants import (
    ASSIGNEE_MISMATCH_ERROR_MESSAGE,
    ASSIGNEE_REQUIRED_ERROR_MESSAGE,
)
from apps.tasks.models import Task, TaskAttachment
from apps.tasks.validators import validate_attachment_size, validate_image_format

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
        # Enforce "exactly one assignee matching assignee_type" on both create and PATCH.
        # On PATCH the payload is partial, so the effective type/assignee is the incoming
        # value if present, otherwise the value already stored on the instance.
        instance = self.instance

        if "assignee_type" in data:
            assignee_type = data["assignee_type"]
        elif instance is not None:
            assignee_type = instance.assignee_type
        else:
            assignee_type = None

        if assignee_type not in _ASSIGNEE_FIELDS:
            return data

        expected_field = _ASSIGNEE_FIELDS[assignee_type]
        for field in _ASSIGNEE_FIELDS.values():
            if field == expected_field:
                effective = (
                    data[field]
                    if field in data
                    else (getattr(instance, field) if instance is not None else None)
                )
                if effective is None:
                    raise serializers.ValidationError(
                        {field: ASSIGNEE_REQUIRED_ERROR_MESSAGE.format(type=assignee_type)}
                    )
            else:
                # client explicitly set a non-matching assignee -> mismatch
                if data.get(field) is not None:
                    raise serializers.ValidationError(
                        {field: ASSIGNEE_MISMATCH_ERROR_MESSAGE.format(type=assignee_type)}
                    )
                # force-null any stale value so the persisted state stays consistent
                data[field] = None
        return data


class TaskAttachmentSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[validate_attachment_size, validate_image_format])

    class Meta:
        model = TaskAttachment
        fields = ["id", "image", "caption", "added_by", "created_at"]
        read_only_fields = ["id", "added_by", "created_at"]
