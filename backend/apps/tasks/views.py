from rest_framework import generics

from apps.tasks.permissions import IsTaskTeamMember, visible_tasks
from apps.tasks.serializers import TaskSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsTaskTeamMember]

    def get_queryset(self):
        return visible_tasks(self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
