"""Schemas partages de DevDocs AI.

Ce module definit le contrat d'interface entre :
- le module de recherche (retrieval/), developpe par Lamiae ;
- le module de generation (rag/), developpe par Aoulia.

Toute modification de ces schemas doit etre validee par les deux
developpeuses, car elle impacte les deux cotes du systeme.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class Technology(StrEnum):
    """Technologies couvertes par DevDocs AI.

    Une question portant sur une autre technologie est hors perimetre.
    """

    PYTHON = "python"
    FASTAPI = "fastapi"
    DOCKER = "docker"
    GIT = "git"
    KUBERNETES = "kubernetes"


class RetrievedChunk(BaseModel):
    """Un passage de documentation retrouve par le module de recherche.

    C'est l'objet que retrieval/ renvoie et que rag/ consomme pour
    construire le contexte du LLM et generer les citations.
    """

    model_config = ConfigDict(
        frozen=True,  # Un passage retrouve ne doit plus etre modifie dans le pipeline.
        extra="forbid",  # Un champ inconnu (ex. faute de frappe) provoque une erreur.
    )

    chunk_id: str = Field(
        min_length=1,
        description="Identifiant unique et stable du passage.",
        examples=["fastapi-tutorial-path-params-003"],
    )
    document_id: str = Field(
        min_length=1,
        description="Identifiant du document source, tel qu'enregistre dans document_manifest.csv.",
    )
    text: str = Field(
        min_length=1,
        description="Contenu du passage, envoye au LLM comme contexte.",
    )
    technology: Technology = Field(
        description="Technologie documentee par ce passage.",
    )
    title: str = Field(
        min_length=1,
        description="Titre de la page de documentation source.",
    )
    section: str | None = Field(
        default=None,
        description="Chemin des titres menant au passage, ex. 'Tutorial > Path Parameters'.",
    )
    source_url: HttpUrl = Field(
        description="URL de la page officielle, utilisee pour les citations.",
    )
    doc_version: str | None = Field(
        default=None,
        description="Version de la documentation (ex. '3.12' pour Python), si elle existe.",
    )
    score: float = Field(
        allow_inf_nan=False,
        description=(
            "Score de pertinence de la derniere etape de recherche (reranker si active). "
            "Son echelle depend de la methode : on ne compare que des scores "
            "produits par la meme configuration."
        ),
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Informations complementaires (strategie de chunking, position, etc.).",
    )

    @field_validator("technology", mode="before")
    @classmethod
    def normalize_technology(cls, value: Any) -> Any:
        """Accepte 'FastAPI' ou ' fastapi ' en les normalisant en 'fastapi'."""
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("text")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        """Refuse un texte compose uniquement d'espaces ou de retours a la ligne."""
        if not value.strip():
            raise ValueError("text ne doit pas etre vide ou compose uniquement d'espaces")
        return value