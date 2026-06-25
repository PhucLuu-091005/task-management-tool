from django.db.models import Q
from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from apps.notifications.services import notify_task_assignment
from apps.tasks.constants import INVALID_FILTER_VALUE_ERROR_MESSAGE
from apps.tasks.models import Task
from apps.tasks.permissions import CanEditTask, visible_tasks
from apps.tasks.serializers import TaskSerializer

_INT_FILTERS = {
    "assignee_user": "assignee_user_id",
    "team": "assignee_team_id",
    "department": "assignee_department_id",
}


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = visible_tasks(self.request.user)
        params = self.request.query_params

        if status := params.get("status"):
            qs = qs.filter(status=status)

        if assignee_type := params.get("assignee_type"):
            qs = qs.filter(assignee_type=assignee_type)

        for param, field in _INT_FILTERS.items():
            raw = params.get(param)
            if raw:
                try:
                    qs = qs.filter(**{field: int(raw)})
                except ValueError as exc:
                    raise ValidationError(
                        INVALID_FILTER_VALUE_ERROR_MESSAGE.format(field=param)
                    ) from exc

        is_overdue = params.get("is_overdue")
        if is_overdue in {"true", "false"}:
            overdue_q = Q(due_date__lt=timezone.now()) & ~Q(status=Task.Status.DONE)
            qs = qs.filter(overdue_q) if is_overdue == "true" else qs.exclude(overdue_q)

        if search := params.get("search"):
            qs = qs.filter(title__icontains=search)

        return qs

    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        notify_task_assignment(task, actor=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [CanEditTask]

    def get_queryset(self):
        return visible_tasks(self.request.user)

    def perform_update(self, serializer):
        instance = serializer.instance
        before = (
            instance.assignee_type,
            instance.assignee_user_id,
            instance.assignee_team_id,
            instance.assignee_department_id,
        )
        task = serializer.save()
        after = (
            task.assignee_type,
            task.assignee_user_id,
            task.assignee_team_id,
            task.assignee_department_id,
        )
        if after != before:
            notify_task_assignment(task, actor=self.request.user)
