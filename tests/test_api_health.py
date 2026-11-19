"""Tests de l'endpoint /health (api/main.py)."""

import pytest
from fastapi.testclient import TestClient

from api.main import API_VERSION, create_app


@pytest.fixture
def client() -> TestClient:
    """Client HTTP de test : envoie des requetes a l'API sans lancer de serveur."""
    return TestClient(create_app())


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": API_VERSION}


def test_unknown_route_returns_404(client):
    response = client.get("/route-inexistante")

    assert response.status_code == 404


def test_openapi_documentation_is_available(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "DevDocs AI"