"""Tests specifiques au MockRetriever (retrieval/mock_retriever.py)."""

import json

import pytest
from pydantic import ValidationError

from core.schemas import Technology
from retrieval.mock_retriever import MockRetriever


def test_loads_all_mock_chunks():
    retriever = MockRetriever()

    assert retriever.chunk_count == 10


def test_most_relevant_chunk_comes_first():
    results = MockRetriever().retrieve("How do I declare a path parameter in FastAPI?")

    assert results[0].chunk_id == "fastapi-path-params-001"
    assert results[0].technology is Technology.FASTAPI


def test_out_of_scope_question_returns_no_chunk():
    results = MockRetriever().retrieve("Quelle est la recette du couscous ?")

    assert results == []


def test_missing_data_file_raises_clear_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        MockRetriever(data_path=tmp_path / "missing.json")


def test_invalid_chunk_in_data_file_is_rejected(tmp_path):
    bad_file = tmp_path / "bad_chunks.json"
    bad_file.write_text(json.dumps([{"chunk_id": "incomplet"}]), encoding="utf-8")

    with pytest.raises(ValidationError):
        MockRetriever(data_path=bad_file)