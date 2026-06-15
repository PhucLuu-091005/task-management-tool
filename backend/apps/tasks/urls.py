from django.urls import path

from apps.tasks.views import TaskListCreateView

urlpatterns = [
    path("", TaskListCreateView.as_view(), name="task-list"),
]
