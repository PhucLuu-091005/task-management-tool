import django_filters

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
        return (
            queryset.filter(status=Task.Status.OVERDUE)
            if value
            else queryset.exclude(status=Task.Status.OVERDUE)
        )
