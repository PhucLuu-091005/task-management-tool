from django.db.models import Count, Q
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

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


def _grouped_counts(qs, field, out_key):
    rows = (
        qs.filter(**{f"{field}__isnull": False})
        .values(field)
        .annotate(count=Count("id", distinct=True))
        .order_by(field)
    )
    return [{out_key: row[field], "count": row["count"]} for row in rows]


class TaskStatsView(APIView):
    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        qs = visible_tasks(request.user)

        by_status = dict.fromkeys(Task.Status.values, 0)
        for row in qs.values("status").annotate(count=Count("id", distinct=True)):
            by_status[row["status"]] = row["count"]

        return Response(
            {
                "total": sum(by_status.values()),
                "by_status": by_status,
                "by_assignee_user": _grouped_counts(qs, "assignee_user", "assignee_user_id"),
                "by_team": _grouped_counts(qs, "assignee_team", "assignee_team_id"),
                "by_department": _grouped_counts(
                    qs, "assignee_department", "assignee_department_id"
                ),
            }
        )
