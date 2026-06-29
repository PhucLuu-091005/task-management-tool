from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.services import notify_task_assignment
from apps.tasks.filters import TaskFilter
from apps.tasks.models import Task
from apps.tasks.permissions import CanEditTask, visible_tasks
from apps.tasks.serializers import TaskSerializer


class TaskPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    pagination_class = TaskPagination

    def get_queryset(self):
        return visible_tasks(self.request.user)

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
