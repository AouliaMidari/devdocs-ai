"""Tests de contrat : toute implementation de Retriever doit les reussir.

Quand le retriever hybride de Lamiae sera pret, il suffira de l'ajouter
a la liste RETRIEVER_FACTORIES pour verifier qu'il respecte le contrat.
"""

import pytest

from core.interfaces import Retriever
from core.schemas import RetrievedChunk, Technology
from retrieval.mock_retriever import MockRetriever

RETRIEVER_FACTORIES = [MockRetriever]

SAMPLE_QUERY = "How do I declare a path parameter in FastAPI?"


@pytest.fixture(params=RETRIEVER_FACTORIES, ids=lambda factory: factory.__name__)
def retriever(request) -> Retriever:
    """Cree une instance de chaque implementation a tester."""
    return request.param()


def test_implements_retriever_interface(retriever):
    assert isinstance(retriever, Retriever)


def test_returns_a_list_of_retrieved_chunks(retriever):
    results = retriever.retrieve(SAMPLE_QUERY)

    assert isinstance(results, list)
    assert results, "Cette question devrait renvoyer au moins un passage"
    assert all(isinstance(chunk, RetrievedChunk) for chunk in results)


@pytest.mark.parametrize("top_k", [1, 3])
def test_respects_top_k(retriever, top_k):
    results = retriever.retrieve("container image build", top_k=top_k)

    assert len(results) <= top_k


def test_results_are_sorted_by_descending_score(retriever):
    results = retriever.retrieve("create a new branch or commit with git", top_k=10)
    scores = [chunk.score for chunk in results]

    assert len(scores) >= 2, "Il faut au moins deux passages pour verifier le tri"
    assert scores == sorted(scores, reverse=True)


def test_technology_filter_is_respected(retriever):
    results = retriever.retrieve("container image", top_k=10, technology=Technology.KUBERNETES)

    assert results, "Ce filtre devrait renvoyer au moins un passage Kubernetes"
    assert all(chunk.technology is Technology.KUBERNETES for chunk in results)


@pytest.mark.parametrize("empty_query", ["", "   "])
def test_empty_query_raises_value_error(retriever, empty_query):
    with pytest.raises(ValueError):
        retriever.retrieve(empty_query)


def test_invalid_top_k_raises_value_error(retriever):
    with pytest.raises(ValueError):
        retriever.retrieve(SAMPLE_QUERY, top_k=0)
