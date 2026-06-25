import pytest
from django.urls import reverse

from apps.notifications.models import Notification

pytestmark = pytest.mark.django_db


def _notif(recipient, task, **kwargs):
    return Notification.objects.create(recipient=recipient, task=task, **kwargs)


def test_list_returns_only_own_notifications(api_client, recipient, other_user, user_task):
    _notif(recipient, user_task)
    _notif(other_user, user_task)
    api_client.force_authenticate(user=recipient)
    res = api_client.get(reverse("notification-list"))
    assert res.status_code == 200
    assert len(res.data) == 1
    assert res.data[0]["task_title"] == user_task.title


def test_list_unread_filter(api_client, recipient, user_task):
    _notif(recipient, user_task, is_read=True)
    _notif(recipient, user_task, is_read=False)
    api_client.force_authenticate(user=recipient)
    res = api_client.get(reverse("notification-list"), {"unread": "true"})
    assert res.status_code == 200
    assert len(res.data) == 1
    assert res.data[0]["is_read"] is False


def test_anonymous_cannot_list(api_client):
    res = api_client.get(reverse("notification-list"))
    assert res.status_code == 401


def test_mark_read(api_client, recipient, user_task):
    n = _notif(recipient, user_task)
    api_client.force_authenticate(user=recipient)
    res = api_client.patch(
        reverse("notification-detail", args=[n.id]), {"is_read": True}, format="json"
    )
    assert res.status_code == 200
    n.refresh_from_db()
    assert n.is_read is True


def test_cannot_touch_others_notification(api_client, recipient, other_user, user_task):
    n = _notif(other_user, user_task)
    api_client.force_authenticate(user=recipient)
    res = api_client.patch(
        reverse("notification-detail", args=[n.id]), {"is_read": True}, format="json"
    )
    assert res.status_code == 404
