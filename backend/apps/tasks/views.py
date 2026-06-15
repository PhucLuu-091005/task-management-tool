from django.db.models import BooleanField, Case, Q, When
from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated

from apps.tasks.constants import INVALID_FILTER_VALUE_ERROR_MESSAGE
from apps.tasks.models import Task
from apps.tasks.permissions import CanEditTask, IsTaskTeamMember, visible_tasks
from apps.tasks.serializers import TaskSerializer


def _validated_int(params, field):
    value = params.get(field)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(
            INVALID_FILTER_VALUE_ERROR_MESSAGE.format(field=field)
        ) from None


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsTaskTeamMember]
    filter_backends = [SearchFilter]
    search_fields = ["title"]

    def get_queryset(self):
        queryset = visible_tasks(self.request.user).annotate(
            overdue=Case(
                When(
                    Q(due_date__isnull=False)
                    & Q(due_date__lt=timezone.now())
                    & ~Q(status=Task.Status.DONE),
                    then=True,
                ),
                default=False,
                output_field=BooleanField(),
            )
        )
        params = self.request.query_params
        status = params.get("status")
        if status:
            queryset = queryset.filter(status=status)
        priority = _validated_int(params, "priority")
        if priority is not None:
            queryset = queryset.filter(priority=priority)
        assignee = _validated_int(params, "assignee")
        if assignee is not None:
            queryset = queryset.filter(assignee_id=assignee)
        is_overdue = params.get("is_overdue")
        if is_overdue is not None:
            queryset = queryset.filter(overdue=is_overdue.lower() == "true")
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return visible_tasks(self.request.user)

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [IsAuthenticated(), CanEditTask()]
        return [IsAuthenticated()]
