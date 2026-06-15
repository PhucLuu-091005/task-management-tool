from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.tasks.permissions import CanEditTask, IsTaskTeamMember, visible_tasks
from apps.tasks.serializers import TaskSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsTaskTeamMember]

    def get_queryset(self):
        return visible_tasks(self.request.user)

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
