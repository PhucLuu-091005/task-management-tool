from django.urls import path

from apps.tasks.views import (
    TaskAttachmentDetailView,
    TaskAttachmentListCreateView,
    TaskDetailView,
    TaskListCreateView,
    TaskStatsView,
)

urlpatterns = [
    path("", TaskListCreateView.as_view(), name="task-list"),
    path("stats/", TaskStatsView.as_view(), name="task-stats"),
    path("<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path(
        "<int:task_id>/attachments/",
        TaskAttachmentListCreateView.as_view(),
        name="task-attachment-list",
    ),
    path(
        "<int:task_id>/attachments/<int:pk>/",
        TaskAttachmentDetailView.as_view(),
        name="task-attachment-detail",
    ),
]
