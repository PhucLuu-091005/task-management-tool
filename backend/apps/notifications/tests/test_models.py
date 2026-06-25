import pytest

from apps.notifications.models import Notification


@pytest.mark.django_db
def test_notification_defaults_unread(user_task, recipient):
    n = Notification.objects.create(recipient=recipient, task=user_task)
    assert n.is_read is False
    assert n.kind == Notification.Kind.TASK_ASSIGNED


@pytest.mark.django_db
def test_notification_str(user_task, recipient):
    n = Notification.objects.create(recipient=recipient, task=user_task)
    assert str(n) == f"task_assigned -> {recipient} (task {user_task.id})"


@pytest.mark.django_db
def test_deleting_task_cascades_notifications(user_task, recipient):
    Notification.objects.create(recipient=recipient, task=user_task)
    user_task.delete()
    assert Notification.objects.count() == 0


@pytest.mark.django_db
def test_ordering_newest_first(user_task, recipient):
    first = Notification.objects.create(recipient=recipient, task=user_task)
    second = Notification.objects.create(recipient=recipient, task=user_task)
    assert list(Notification.objects.all()) == [second, first]
