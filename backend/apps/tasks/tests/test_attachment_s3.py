import boto3
import pytest
from moto import mock_aws

from apps.tasks.models import TaskAttachment
from apps.tasks.tests.helpers import team_task
from apps.tasks.tests.test_attachments import _image_upload, _list_url

pytestmark = pytest.mark.django_db

BUCKET = "test-attachments"


@pytest.fixture
def s3_bucket(settings, monkeypatch):
    for key in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
        monkeypatch.setenv(key, "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    with mock_aws():
        boto3.client("s3", region_name="us-east-1").create_bucket(Bucket=BUCKET)
        settings.STORAGES = {
            **settings.STORAGES,
            "default": {
                "BACKEND": "storages.backends.s3.S3Storage",
                "OPTIONS": {
                    "bucket_name": BUCKET,
                    "region_name": "us-east-1",
                    "signature_version": "s3v4",
                    "default_acl": None,
                    "querystring_auth": True,
                    "querystring_expire": 3600,
                    "file_overwrite": False,
                },
            },
        }
        yield


def test_attachment_uploads_to_s3(member_client, team, creator, s3_bucket):
    task = team_task(creator, team)

    res = member_client.post(_list_url(task), {"image": _image_upload()}, format="multipart")

    assert res.status_code == 201
    att = TaskAttachment.objects.get(id=res.data["id"])
    assert att.image.storage.__class__.__name__ == "S3Storage"
    assert att.image.storage.exists(att.image.name)


def test_attachment_url_is_presigned(member_client, team, creator, s3_bucket):
    task = team_task(creator, team)
    res = member_client.post(_list_url(task), {"image": _image_upload()}, format="multipart")

    url = TaskAttachment.objects.get(id=res.data["id"]).image.url

    assert url.startswith("https://")
    assert BUCKET in url
    assert "Signature" in url and "Expires" in url
