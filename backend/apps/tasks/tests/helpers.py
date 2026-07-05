from apps.tasks.models import Task


def team_task(creator, team, **kwargs):
    kwargs.setdefault("title", "Task")
    return Task.objects.create(
        created_by=creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=team,
        **kwargs,
    )
