"""Retriever factice pour developper le pipeline RAG sans les vrais documents.

Son score est volontairement tres simple : la proportion des mots de la
question presents dans le passage. Ce n'est PAS BM25. Il sert uniquement
a tester le reste du systeme en attendant le retriever hybride de Lamiae.
"""

import json
import re
from pathlib import Path

from core.schemas import RetrievedChunk, Technology

# Chemin calcule a partir de l'emplacement de ce fichier : aucun chemin code en dur.
DEFAULT_DATA_PATH = Path(__file__).parent / "mock_chunks.json"

# Mots trop frequents pour aider a distinguer les passages.
STOPWORDS = frozenset(
    {
        "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "in",
        "is", "it", "of", "on", "or", "the", "to", "what", "with", "you",
    }
)


def tokenize(text: str) -> set[str]:
    """Decoupe un texte en mots en minuscules, sans les mots vides."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {word for word in words if word not in STOPWORDS}


class MockRetriever:
    """Implementation factice de l'interface Retriever (core/interfaces.py)."""

    def __init__(self, data_path: Path = DEFAULT_DATA_PATH) -> None:
        self._chunks = self._load_chunks(data_path)

    @staticmethod
    def _load_chunks(data_path: Path) -> list[RetrievedChunk]:
        """Charge et valide les passages factices des le demarrage."""
        try:
            raw_items = json.loads(data_path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise FileNotFoundError(f"Fichier de passages factices introuvable : {data_path}") from error
        except json.JSONDecodeError as error:
            raise ValueError(f"JSON invalide dans {data_path} : {error}") from error

        # Le vrai score est calcule pour chaque question ; 0.0 sert seulement a valider le reste.
        return [RetrievedChunk(**item, score=0.0) for item in raw_items]

    @property
    def chunk_count(self) -> int:
        """Nombre de passages factices charges."""
        return len(self._chunks)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        technology: Technology | None = None,
    ) -> list[RetrievedChunk]:
        """Renvoie les passages qui partagent le plus de mots avec la question."""
        if not query or not query.strip():
            raise ValueError("query ne doit pas etre vide")
        if top_k < 1:
            raise ValueError("top_k doit etre superieur ou egal a 1")

        query_words = tokenize(query)
        if not query_words:
            return []

        scored_chunks: list[RetrievedChunk] = []
        for chunk in self._chunks:
            if technology is not None and chunk.technology != technology:
                continue

            chunk_words = tokenize(f"{chunk.title} {chunk.section or ''} {chunk.text}")
            overlap = len(query_words & chunk_words)
            if overlap == 0:
                continue

            score = overlap / len(query_words)
            # RetrievedChunk est immuable : on cree une copie avec le nouveau score.
            scored_chunks.append(chunk.model_copy(update={"score": score}))

        scored_chunks.sort(key=lambda chunk: chunk.score, reverse=True)
        return scored_chunks[:top_k]