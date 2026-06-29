import django_filters
from django.db.models import Q
from django.utils import timezone

from apps.tasks.models import Task


class TaskFilter(django_filters.FilterSet):
    team = django_filters.NumberFilter(field_name="assignee_team")
    department = django_filters.NumberFilter(field_name="assignee_department")
    assignee_user = django_filters.NumberFilter(field_name="assignee_user")
    is_overdue = django_filters.BooleanFilter(method="filter_is_overdue")

    class Meta:
        model = Task
        fields = ["status", "priority", "assignee_type", "assignee_user", "team", "department"]

    def filter_is_overdue(self, queryset, name, value):
        overdue = Q(due_date__lt=timezone.now()) & ~Q(status=Task.Status.DONE)
        return queryset.filter(overdue) if value else queryset.exclude(overdue)
