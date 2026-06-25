from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source="task.title", read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "task", "task_title", "kind", "is_read", "created_at"]
        read_only_fields = ["id", "task", "task_title", "kind", "created_at"]
