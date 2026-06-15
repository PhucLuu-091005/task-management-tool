from django.urls import path

from apps.tasks.views import TaskDetailView, TaskListCreateView

urlpatterns = [
    path("", TaskListCreateView.as_view(), name="task-list"),
    path("<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
]
