import os
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from apps.tasks.models import Task, TaskAttachment

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _media_root(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)


def _team_task(creator, team):
    return Task.objects.create(
        title="Task",
        created_by=creator,
        assignee_type=Task.AssigneeType.TEAM,
        assignee_team=team,
    )


def _png_bytes(fmt="PNG"):
    buf = BytesIO()
    Image.new("RGB", (10, 10), "blue").save(buf, format=fmt)
    buf.seek(0)
    return buf


def _image_upload(name="shot.png", fmt="PNG", content_type="image/png"):
    return SimpleUploadedFile(name, _png_bytes(fmt).read(), content_type=content_type)


def _oversized_upload():
    # Random pixels resist PNG compression, so the encoded file exceeds the 5 MB cap.
    side = 1500
    img = Image.frombytes("RGB", (side, side), os.urandom(side * side * 3))
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return SimpleUploadedFile("big.png", buf.read(), content_type="image/png")


def _list_url(task):
    return reverse("task-attachment-list", args=[task.id])


def test_upload_attachment(member_client, team_member, team, creator):
    task = _team_task(creator, team)

    res = member_client.post(
        _list_url(task), {"image": _image_upload(), "caption": "before"}, format="multipart"
    )

    assert res.status_code == 201
    att = TaskAttachment.objects.get(id=res.data["id"])
    assert att.task_id == task.id
    assert att.added_by_id == team_member.id
    assert att.caption == "before"


def test_list_attachments_for_task(member_client, team, creator):
    task = _team_task(creator, team)
    TaskAttachment.objects.create(task=task, added_by=creator, image="task_attachments/a.png")

    res = member_client.get(_list_url(task))

    assert res.status_code == 200
    assert len(res.data) == 1


def test_upload_rejects_oversized_image(member_client, team, creator):
    task = _team_task(creator, team)

    res = member_client.post(_list_url(task), {"image": _oversized_upload()}, format="multipart")

    assert res.status_code == 400
    assert "image" in res.data


def test_upload_rejects_non_image(member_client, team, creator):
    task = _team_task(creator, team)
    text = SimpleUploadedFile("note.txt", b"not an image", content_type="text/plain")

    res = member_client.post(_list_url(task), {"image": text}, format="multipart")

    assert res.status_code == 400


def test_upload_rejects_disallowed_format(member_client, team, creator):
    task = _team_task(creator, team)
    bmp = _image_upload(name="pic.bmp", fmt="BMP", content_type="image/bmp")

    res = member_client.post(_list_url(task), {"image": bmp}, format="multipart")

    assert res.status_code == 400


def test_attachments_scoped_to_visible_task(member_client, other_team, creator):
    hidden = _team_task(creator, other_team)

    res = member_client.get(_list_url(hidden))

    assert res.status_code == 404


def test_uploader_can_delete_own_attachment(member_client, team_member, team, creator):
    task = _team_task(creator, team)
    att = TaskAttachment.objects.create(
        task=task, added_by=team_member, image="task_attachments/a.png"
    )

    res = member_client.delete(reverse("task-attachment-detail", args=[task.id, att.id]))

    assert res.status_code == 204


def test_member_cannot_delete_others_attachment(member_client, team, creator, admin_user):
    task = _team_task(creator, team)
    att = TaskAttachment.objects.create(
        task=task, added_by=admin_user, image="task_attachments/a.png"
    )

    res = member_client.delete(reverse("task-attachment-detail", args=[task.id, att.id]))

    assert res.status_code == 403


def test_leader_can_delete_any_attachment(leader_client, team, creator, admin_user):
    task = _team_task(creator, team)
    att = TaskAttachment.objects.create(
        task=task, added_by=admin_user, image="task_attachments/a.png"
    )

    res = leader_client.delete(reverse("task-attachment-detail", args=[task.id, att.id]))

    assert res.status_code == 204


def test_department_lead_can_delete_any_attachment(dept_lead_client, team, creator, admin_user):
    task = _team_task(creator, team)
    att = TaskAttachment.objects.create(
        task=task, added_by=admin_user, image="task_attachments/a.png"
    )

    res = dept_lead_client.delete(reverse("task-attachment-detail", args=[task.id, att.id]))

    assert res.status_code == 204


def test_admin_can_delete_any_attachment(admin_client, team, creator, team_member):
    task = _team_task(creator, team)
    att = TaskAttachment.objects.create(
        task=task, added_by=team_member, image="task_attachments/a.png"
    )

    res = admin_client.delete(reverse("task-attachment-detail", args=[task.id, att.id]))

    assert res.status_code == 204


def test_upload_rejects_oversized_dimensions(member_client, team, creator, monkeypatch):
    monkeypatch.setattr("apps.tasks.validators.MAX_IMAGE_PIXELS", 10)
    task = _team_task(creator, team)

    res = member_client.post(_list_url(task), {"image": _image_upload()}, format="multipart")

    assert res.status_code == 400
    assert "image" in res.data


def test_unauthenticated_cannot_delete(api_client, team, creator):
    task = _team_task(creator, team)
    att = TaskAttachment.objects.create(task=task, added_by=creator, image="task_attachments/a.png")

    res = api_client.delete(reverse("task-attachment-detail", args=[task.id, att.id]))

    assert res.status_code in (401, 403)


def test_delete_via_wrong_task_url_is_404(member_client, team_member, team, creator):
    task_a = _team_task(creator, team)
    task_b = _team_task(creator, team)
    att = TaskAttachment.objects.create(
        task=task_b, added_by=team_member, image="task_attachments/a.png"
    )

    res = member_client.delete(reverse("task-attachment-detail", args=[task_a.id, att.id]))

    assert res.status_code == 404


def test_saved_image_is_intact(member_client, team, creator):
    task = _team_task(creator, team)
    data = _png_bytes().read()
    upload = SimpleUploadedFile("shot.png", data, content_type="image/png")

    res = member_client.post(_list_url(task), {"image": upload}, format="multipart")

    att = TaskAttachment.objects.get(id=res.data["id"])
    assert att.image.size == len(data)
