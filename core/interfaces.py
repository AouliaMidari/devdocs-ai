"""Interfaces partagees de DevDocs AI.

Une interface decrit CE QU'un composant doit faire, sans dire COMMENT.
Le pipeline rag/ depend uniquement de ces interfaces, jamais d'une
implementation precise : on pourra remplacer le MockRetriever par le
retriever hybride de Lamiae sans modifier le pipeline RAG.
"""

from typing import Protocol, runtime_checkable

from core.schemas import RetrievedChunk, Technology


@runtime_checkable
class Retriever(Protocol):
    """Contrat que doit respecter tout module de recherche.

    Regles du contrat (verifiees par tests/test_retriever_contract.py) :
    1. Renvoie une liste de RetrievedChunk, eventuellement vide, jamais None.
    2. Renvoie au maximum top_k passages.
    3. Les passages sont tries par score decroissant.
    4. Si technology est fourni, tous les passages concernent cette technologie.
    5. Leve ValueError si la question est vide ou si top_k < 1.
    """

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        technology: Technology | None = None,
    ) -> list[RetrievedChunk]:
        """Retrouve les passages les plus pertinents pour une question."""
        ...
