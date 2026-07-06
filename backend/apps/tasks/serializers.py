from django.core.validators import URLValidator
from django.db import transaction
from rest_framework import serializers

from apps.tasks.constants import (
    ASSIGNEE_MISMATCH_ERROR_MESSAGE,
    ASSIGNEE_REQUIRED_ERROR_MESSAGE,
    INVALID_STATUS_TRANSITION_ERROR_MESSAGE,
    MANUAL_STATUSES,
)
from apps.tasks.models import (
    TASK_LINK_URL_MAX_LENGTH,
    Task,
    TaskAttachment,
    TaskLink,
    TaskStatusEvent,
)
from apps.tasks.validators import validate_attachment_size, validate_image_format

_ASSIGNEE_FIELDS = {
    Task.AssigneeType.USER: "assignee_user",
    Task.AssigneeType.TEAM: "assignee_team",
    Task.AssigneeType.DEPARTMENT: "assignee_department",
}


def _user_display_name(user) -> str:
    # Vietnamese name order: family name first.
    return f"{user.last_name} {user.first_name}".strip() or user.username


class TaskStatusEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatusEvent
        fields = ["id", "from_status", "to_status", "changed_by", "changed_at"]
        read_only_fields = fields


class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.BooleanField(read_only=True)
    assignee_user_name = serializers.SerializerMethodField()
    assignee_team_name = serializers.SerializerMethodField()
    assignee_department_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    started_at = serializers.SerializerMethodField()
    completed_at = serializers.SerializerMethodField()
    status_events = TaskStatusEventSerializer(many=True, read_only=True)

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
            "assignee_user_name",
            "assignee_team",
            "assignee_team_name",
            "assignee_department",
            "assignee_department_name",
            "created_by",
            "created_by_name",
            "due_date",
            "is_overdue",
            "assigned_at",
            "started_at",
            "completed_at",
            "status_events",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_by",
            "assigned_at",
            "created_at",
            "updated_at",
        ]

    def get_started_at(self, obj):
        # First entry into in_progress; None until the task is started.
        events = [e for e in obj.status_events.all() if e.to_status == Task.Status.IN_PROGRESS]
        return events[0].changed_at if events else None

    def get_completed_at(self, obj):
        # Latest entry into done; a reopened-then-redone task keeps the most recent.
        events = [e for e in obj.status_events.all() if e.to_status == Task.Status.DONE]
        return events[-1].changed_at if events else None

    def get_assignee_user_name(self, obj) -> str | None:
        return _user_display_name(obj.assignee_user) if obj.assignee_user_id else None

    def get_assignee_team_name(self, obj) -> str | None:
        return obj.assignee_team.name if obj.assignee_team_id else None

    def get_assignee_department_name(self, obj) -> str | None:
        return obj.assignee_department.name if obj.assignee_department_id else None

    def get_created_by_name(self, obj) -> str:
        return _user_display_name(obj.created_by)

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


class TaskStatusSerializer(serializers.ModelSerializer):
    # overdue is system-managed (flip_overdue_tasks); users pick from the manual lifecycle only.
    status = serializers.ChoiceField(choices=MANUAL_STATUSES)

    class Meta:
        model = Task
        fields = ["status"]

    def validate_status(self, value: str) -> str:
        current = self.instance.status
        if not Task.can_transition(current, value):
            raise serializers.ValidationError(
                INVALID_STATUS_TRANSITION_ERROR_MESSAGE.format(from_status=current, to_status=value)
            )
        return value

    def update(self, instance, validated_data):
        to_status = validated_data["status"]
        with transaction.atomic():
            # Re-read under a row lock and re-validate: status may have changed
            # (e.g. a concurrent overdue flip) between get_object() and here, so
            # the transition and its recorded from_status stay consistent.
            locked = Task.objects.select_for_update().get(pk=instance.pk)
            if not Task.can_transition(locked.status, to_status):
                raise serializers.ValidationError(
                    INVALID_STATUS_TRANSITION_ERROR_MESSAGE.format(
                        from_status=locked.status, to_status=to_status
                    )
                )
            from_status = locked.status
            # Scope the write to the field this endpoint owns; a full instance.save()
            # would persist the stale get_object() snapshot and clobber a concurrent
            # edit to title/description/assignee committed after get_object().
            instance.status = to_status
            instance.save(update_fields=["status", "updated_at"])
            TaskStatusEvent.objects.create(
                task=instance,
                from_status=from_status,
                to_status=to_status,
                changed_by=self.context["request"].user,
            )
        return instance


class TaskLinkSerializer(serializers.ModelSerializer):
    # DRF strips model-level URLValidators, so the scheme allowlist must live here.
    url = serializers.URLField(
        max_length=TASK_LINK_URL_MAX_LENGTH,
        validators=[URLValidator(schemes=["http", "https"])],
    )

    class Meta:
        model = TaskLink
        fields = ["id", "url", "label", "added_by", "created_at"]
        read_only_fields = ["id", "added_by", "created_at"]


class TaskAttachmentSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[validate_attachment_size, validate_image_format])

    class Meta:
        model = TaskAttachment
        fields = ["id", "image", "caption", "added_by", "created_at"]
        read_only_fields = ["id", "added_by", "created_at"]
