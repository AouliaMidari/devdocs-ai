"""Tests du contrat d'interface RetrievedChunk (core/schemas.py)."""

import pytest
from pydantic import ValidationError

from core.schemas import RetrievedChunk, Technology


@pytest.fixture
def valid_chunk_data() -> dict:
    """Donnees d'un passage valide, que chaque test peut modifier."""
    return {
        "chunk_id": "fastapi-tutorial-path-params-003",
        "document_id": "fastapi/tutorial/path-params.md",
        "text": "Path parameters are declared in the route path with curly braces, like {item_id}.",
        "technology": "fastapi",
        "title": "Path Parameters",
        "section": "Tutorial > Path Parameters",
        "source_url": "https://fastapi.tiangolo.com/tutorial/path-params/",
        "doc_version": None,
        "score": 0.87,
    }


def test_valid_chunk_is_accepted(valid_chunk_data):
    chunk = RetrievedChunk(**valid_chunk_data)

    assert chunk.chunk_id == "fastapi-tutorial-path-params-003"
    assert chunk.technology is Technology.FASTAPI
    assert str(chunk.source_url) == "https://fastapi.tiangolo.com/tutorial/path-params/"
    assert chunk.metadata == {}


def test_technology_is_normalized(valid_chunk_data):
    valid_chunk_data["technology"] = "  FastAPI "

    chunk = RetrievedChunk(**valid_chunk_data)

    assert chunk.technology is Technology.FASTAPI


def test_unknown_technology_is_rejected(valid_chunk_data):
    valid_chunk_data["technology"] = "java"

    with pytest.raises(ValidationError):
        RetrievedChunk(**valid_chunk_data)


def test_missing_source_url_is_rejected(valid_chunk_data):
    del valid_chunk_data["source_url"]

    with pytest.raises(ValidationError):
        RetrievedChunk(**valid_chunk_data)


def test_local_path_as_source_url_is_rejected(valid_chunk_data):
    valid_chunk_data["source_url"] = "data/raw/fastapi/tutorial/path-params.md"

    with pytest.raises(ValidationError):
        RetrievedChunk(**valid_chunk_data)


@pytest.mark.parametrize("blank_text", ["", "   ", "\n\t"])
def test_blank_text_is_rejected(valid_chunk_data, blank_text):
    valid_chunk_data["text"] = blank_text

    with pytest.raises(ValidationError):
        RetrievedChunk(**valid_chunk_data)


def test_nan_score_is_rejected(valid_chunk_data):
    valid_chunk_data["score"] = float("nan")

    with pytest.raises(ValidationError):
        RetrievedChunk(**valid_chunk_data)


def test_unknown_field_is_rejected(valid_chunk_data):
    valid_chunk_data["sourceurl"] = "https://example.com"  # Faute de frappe volontaire.

    with pytest.raises(ValidationError):
        RetrievedChunk(**valid_chunk_data)


def test_chunk_is_immutable(valid_chunk_data):
    chunk = RetrievedChunk(**valid_chunk_data)

    with pytest.raises(ValidationError):
        chunk.text = "texte modifie"