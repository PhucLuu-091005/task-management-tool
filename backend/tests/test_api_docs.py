import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


def test_openapi_schema_is_served_without_auth(client):
    res = client.get("/api/schema/")
    assert res.status_code == 200
    assert b"openapi" in res.content


def test_swagger_ui_is_served_without_auth(client):
    res = client.get("/api/docs/")
    assert res.status_code == 200


def test_schema_documents_task_endpoints(client):
    res = client.get("/api/schema/")
    assert b"/api/tasks/" in res.content


def test_schema_documents_stats_endpoint(client):
    res = client.get("/api/schema/")
    assert b"/api/tasks/stats/" in res.content
