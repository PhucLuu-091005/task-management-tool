import os
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _media_root(settings, tmp_path):
    # Never write uploads into the real media dir during tests.
    settings.MEDIA_ROOT = str(tmp_path)


def _image_bytes(fmt="PNG"):
    buf = BytesIO()
    Image.new("RGB", (24, 24), "green").save(buf, format=fmt)
    buf.seek(0)
    return buf


def _image_upload(name="me.png", fmt="PNG", content_type="image/png"):
    return SimpleUploadedFile(name, _image_bytes(fmt).read(), content_type=content_type)


def _oversized_upload():
    # Random pixels resist PNG compression, so the encoded file exceeds the 2 MB cap.
    side = 1200
    img = Image.frombytes("RGB", (side, side), os.urandom(side * side * 3))
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return SimpleUploadedFile("big.png", buf.read(), content_type="image/png")


def test_profile_avatar_null_by_default(auth_client, profile_url):
    res = auth_client.get(profile_url)

    assert res.status_code == 200
    assert res.data["avatar"] is None


def test_upload_avatar_sets_it(auth_client, profile_url, user):
    res = auth_client.patch(profile_url, {"avatar": _image_upload()}, format="multipart")

    assert res.status_code == 200
    assert res.data["avatar"]
    user.refresh_from_db()
    assert user.avatar


def test_uploaded_avatar_url_is_root_relative(auth_client, profile_url):
    res = auth_client.patch(profile_url, {"avatar": _image_upload()}, format="multipart")

    # A root-relative /media/... URL rides the frontend proxy in dev; prod S3
    # returns its own absolute URL, so we only assert the dev shape here.
    assert res.data["avatar"].startswith("/media/avatars/")


def test_upload_avatar_requires_auth(api_client, profile_url):
    res = api_client.patch(profile_url, {"avatar": _image_upload()}, format="multipart")

    assert res.status_code == 401


def test_upload_rejects_oversized_image(auth_client, profile_url):
    res = auth_client.patch(profile_url, {"avatar": _oversized_upload()}, format="multipart")

    assert res.status_code == 400
    assert "avatar" in res.data


def test_upload_rejects_non_image(auth_client, profile_url):
    text = SimpleUploadedFile("note.txt", b"not an image", content_type="text/plain")

    res = auth_client.patch(profile_url, {"avatar": text}, format="multipart")

    assert res.status_code == 400
    assert "avatar" in res.data


def test_upload_rejects_disallowed_format(auth_client, profile_url):
    bmp = _image_upload(name="pic.bmp", fmt="BMP", content_type="image/bmp")

    res = auth_client.patch(profile_url, {"avatar": bmp}, format="multipart")

    assert res.status_code == 400
    assert "avatar" in res.data


def test_upload_rejects_oversized_dimensions(auth_client, profile_url, monkeypatch):
    monkeypatch.setattr("apps.users.validators.MAX_IMAGE_PIXELS", 10)

    res = auth_client.patch(profile_url, {"avatar": _image_upload()}, format="multipart")

    assert res.status_code == 400
    assert "avatar" in res.data


def test_remove_avatar_clears_it(auth_client, profile_url, user):
    auth_client.patch(profile_url, {"avatar": _image_upload()}, format="multipart")
    user.refresh_from_db()
    old_path = user.avatar.path
    assert os.path.exists(old_path)

    res = auth_client.patch(profile_url, {"avatar": None}, format="json")

    assert res.status_code == 200
    assert res.data["avatar"] is None
    user.refresh_from_db()
    assert not user.avatar
    # Clearing must also drop the stored file, not just the DB reference.
    assert not os.path.exists(old_path)


def test_replacing_avatar_deletes_old_file(auth_client, profile_url, user):
    auth_client.patch(profile_url, {"avatar": _image_upload(name="first.png")}, format="multipart")
    user.refresh_from_db()
    old_path = user.avatar.path
    assert os.path.exists(old_path)

    auth_client.patch(profile_url, {"avatar": _image_upload(name="second.png")}, format="multipart")

    assert not os.path.exists(old_path)


def test_replacing_avatar_returns_new_url(auth_client, profile_url):
    first = auth_client.patch(
        profile_url, {"avatar": _image_upload(name="first.png")}, format="multipart"
    )
    second = auth_client.patch(
        profile_url, {"avatar": _image_upload(name="second.png")}, format="multipart"
    )

    # Cleaning up the replaced file must not null the response's avatar.
    assert second.data["avatar"]
    assert second.data["avatar"] != first.data["avatar"]


def test_upload_avatar_does_not_touch_other_fields(auth_client, profile_url, user):
    res = auth_client.patch(profile_url, {"avatar": _image_upload()}, format="multipart")

    assert res.status_code == 200
    # The write path only touches the avatar; identity fields stay intact.
    assert res.data["email"] == user.email
    assert res.data["username"] == user.username
