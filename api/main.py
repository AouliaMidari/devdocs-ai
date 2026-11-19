"""Point d'entree de l'API REST de DevDocs AI.

Lancer le serveur de developpement depuis la racine du projet :
    python -m uvicorn api.main:app --reload
"""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

API_VERSION = "0.1.0"


class HealthResponse(BaseModel):
    """Reponse de l'endpoint /health."""

    status: Literal["ok"]
    version: str


def create_app() -> FastAPI:
    """Construit et configure l'application FastAPI.

    Une fonction "usine" (factory) permet de creer une application neuve
    pour chaque test, et plus tard d'y brancher le MockRetriever ou le
    vrai retriever selon la configuration.
    """
    app = FastAPI(
        title="DevDocs AI",
        description=(
            "Assistant RAG pour la documentation officielle de Python, "
            "FastAPI, Docker, Git et Kubernetes."
        ),
        version=API_VERSION,
    )

    @app.get("/health", response_model=HealthResponse, tags=["monitoring"])
    def health() -> HealthResponse:
        """Indique que l'API est en vie. Utilise par Docker, Kubernetes et la CI."""
        return HealthResponse(status="ok", version=API_VERSION)

    return app


app = create_app()