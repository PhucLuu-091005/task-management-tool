import pytest
from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.validation import validate_schema
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
    assert b"swagger-ui" in res.content


def test_generated_schema_is_valid_openapi():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    validate_schema(schema)


def test_schema_documents_task_crud_and_stats():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    paths = schema["paths"]
    assert "/api/tasks/" in paths
    assert "/api/tasks/{id}/" in paths
    assert "/api/tasks/stats/" in paths


def test_schema_documents_logout_request_body():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    assert "LogoutRequest" in schema["components"]["schemas"]
