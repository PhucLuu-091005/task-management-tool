from apps.notifications.models import Notification
from apps.tasks.models import Task
from apps.teams.models import TeamMembership


def recipients_for_assignment(task):
    if task.assignee_type == Task.AssigneeType.USER:
        return [task.assignee_user] if task.assignee_user_id else []
    if task.assignee_type == Task.AssigneeType.TEAM:
        if not task.assignee_team_id:
            return []
        leader_ids = TeamMembership.objects.filter(
            team_id=task.assignee_team_id, role=TeamMembership.Role.LEADER
        ).values_list("user_id", flat=True)
        from django.contrib.auth import get_user_model

        return list(get_user_model().objects.filter(id__in=leader_ids))
    if task.assignee_type == Task.AssigneeType.DEPARTMENT:
        if task.assignee_department_id and task.assignee_department.lead_id:
            return [task.assignee_department.lead]
        return []
    return []


def notify_task_assignment(task, actor=None) -> int:
    actor_id = actor.id if actor is not None else None
    seen: set[int] = set()
    to_create = []
    for user in recipients_for_assignment(task):
        if user is None or user.id == actor_id or user.id in seen:
            continue
        seen.add(user.id)
        to_create.append(
            Notification(recipient=user, task=task, kind=Notification.Kind.TASK_ASSIGNED)
        )
    Notification.objects.bulk_create(to_create)
    return len(to_create)
