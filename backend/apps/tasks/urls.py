from django.urls import path

from apps.tasks.views import TaskDetailView, TaskListCreateView, TaskStatsView

urlpatterns = [
    path("", TaskListCreateView.as_view(), name="task-list"),
    path("stats/", TaskStatsView.as_view(), name="task-stats"),
    path("<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
]
