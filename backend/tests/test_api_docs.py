import pytest
from drf_spectacular.generators import SchemaGenerator
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


def test_docs_are_open_in_development(client):
    assert client.get("/api/schema/").status_code == 200
    assert client.get("/api/docs/").status_code == 200


def test_schema_documents_task_crud_and_stats():
    paths = SchemaGenerator().get_schema(request=None, public=True)["paths"]
    assert "/api/tasks/" in paths
    assert "/api/tasks/{id}/" in paths
    assert "/api/tasks/stats/" in paths


def test_schema_documents_cookie_based_logout():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    # Logout is cookie-based now: no request body, no LogoutRequest schema.
    assert "LogoutRequest" not in schema["components"]["schemas"]
    assert "requestBody" not in schema["paths"]["/api/users/logout/"]["post"]


def test_schema_documents_access_only_token_responses():
    schemas = SchemaGenerator().get_schema(request=None, public=True)["components"]["schemas"]
    assert "AccessTokenResponse" in schemas
    assert "access" in schemas["AccessTokenResponse"]["properties"]
    assert "refresh" not in schemas["AccessTokenResponse"]["properties"]
