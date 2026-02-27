"""
semantic_retrieval — Embedding-based wisdom retrieval
=====================================================

Provides semantic similarity matching for THEOS wisdom stores.  A layered
abstraction lets you swap the storage backend without changing calling code:

.. code-block:: text

    EmbeddingAdapter          ← generates vectors (mock / OpenAI / HF)
         │
    VectorStore (ABC)         ← abstract interface for add / search / persist
         │
    ├── InMemoryVectorStore   ← pure-Python, no deps  (default)
    ├── ChromaVectorStore     ← chromadb backend  (pip install chromadb)
    └── FAISSVectorStore      ← FAISS backend     (pip install faiss-cpu)

Factory::

    store = get_vector_store("memory")            # no deps
    store = get_vector_store("chroma", path="./wisdom_db")
    store = get_vector_store("faiss",  path="./wisdom.index")

Integration with :class:`~theos_core.TheosCore`::

    from semantic_retrieval import get_vector_store, MockEmbeddingAdapter

    store = get_vector_store("memory", embedding=MockEmbeddingAdapter(384))

    def retrieve_wisdom(query, W, threshold):
        return store.search(query, top_k=5, threshold=threshold)

    def update_wisdom(W, query, output, confidence):
        store.add({"query": query, "output": str(output), "confidence": confidence})
        return W + [{"query": query, "output": str(output), "confidence": confidence}]

Author: Frederick Davis Stalnecker
Date:   February 2026
"""

from __future__ import annotations

import json
import math
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# Embeddings
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class EmbeddingVector:
    """A dense vector representation of a piece of text.

    Attributes:
        text:   Original text that was embedded.
        vector: Dense float vector.
    """

    text: str
    vector: list[float]

    def __post_init__(self) -> None:
        if not self.vector:
            raise ValueError("EmbeddingVector cannot be empty")

    @property
    def dimension(self) -> int:
        return len(self.vector)


class EmbeddingAdapter(ABC):
    """Abstract base class for embedding providers.

    Subclass and implement :meth:`_embed` to plug in any embedding model.
    Results are cached in-memory to avoid redundant API calls.
    """

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._cache: dict[str, list[float]] = {}

    def embed(self, text: str) -> EmbeddingVector:
        """Return an :class:`EmbeddingVector` for *text*, using cache."""
        if text not in self._cache:
            self._cache[text] = self._embed(text)
        return EmbeddingVector(text=text, vector=self._cache[text])

    @abstractmethod
    def _embed(self, text: str) -> list[float]:
        """Generate a raw float vector for *text*."""

    def clear_cache(self) -> None:
        self._cache.clear()


class MockEmbeddingAdapter(EmbeddingAdapter):
    """Deterministic embedding adapter for tests and offline use.

    Generates a unit-normalised vector based on the text's hash, ensuring:

    * Same input  → same output (deterministic).
    * Different inputs → different outputs (hash mixing).
    * Zero external dependencies.

    Args:
        dimension: Embedding dimensionality (default 384, matching
            ``sentence-transformers/all-MiniLM-L6-v2``).
    """

    def __init__(self, dimension: int = 384) -> None:
        super().__init__(model_name="mock-embedding")
        self.dimension = dimension

    def _embed(self, text: str) -> list[float]:
        h = hash(text)
        vec = [math.sin((h + i * 12_345) / 10_000.0) for i in range(self.dimension)]
        mag = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / mag for v in vec]


# ─────────────────────────────────────────────────────────────────────────────
# VectorStore — abstract interface
# ─────────────────────────────────────────────────────────────────────────────


class VectorStore(ABC):
    """Abstract interface for vector stores used by the THEOS wisdom layer.

    A ``VectorStore`` holds wisdom records (arbitrary dicts with at least a
    ``"query"`` key) and provides semantic search via embedding similarity.

    Implementations
    ---------------
    * :class:`InMemoryVectorStore` — pure Python, no deps.
    * :class:`ChromaVectorStore`   — persistent, requires ``chromadb``.
    * :class:`FAISSVectorStore`    — high-perf, requires ``faiss-cpu``.
    """

    @abstractmethod
    def add(self, record: dict[str, Any]) -> None:
        """Persist one wisdom record.

        Args:
            record: Dict containing at least ``"query"`` (str).
        """

    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7,
    ) -> list[dict[str, Any]]:
        """Return the *top_k* most similar records above *threshold*.

        Each returned dict is a copy of the stored record augmented with a
        ``"similarity_score"`` key (float in [0, 1]).

        Args:
            query:     Free-text query.
            top_k:     Maximum results.
            threshold: Minimum cosine similarity (0 – 1).
        """

    @abstractmethod
    def persist(self, path: str) -> None:
        """Serialise the store to *path*.

        Args:
            path: File or directory path (backend-specific).
        """

    @classmethod
    @abstractmethod
    def load(
        cls,
        path: str,
        embedding_adapter: EmbeddingAdapter,
    ) -> VectorStore:
        """Deserialise a previously :meth:`persist`-ed store from *path*."""

    @abstractmethod
    def __len__(self) -> int:
        """Number of records in the store."""

    def get_statistics(self) -> dict[str, Any]:
        """Return basic store statistics. Override for backend-specific metrics."""
        return {"records": len(self), "backend": type(self).__name__}

    def __repr__(self) -> str:
        return f"{type(self).__name__}(records={len(self)})"


# ─────────────────────────────────────────────────────────────────────────────
# InMemoryVectorStore — pure Python, no dependencies
# ─────────────────────────────────────────────────────────────────────────────


class InMemoryVectorStore(VectorStore):
    """Pure-Python in-memory vector store.  Zero external dependencies.

    Uses cosine similarity on normalised dense vectors produced by any
    :class:`EmbeddingAdapter`.  Suitable for development, unit tests, and
    small wisdom stores (< ~10 k records).

    Args:
        embedding_adapter: Adapter used to embed query and record texts.
    """

    def __init__(self, embedding_adapter: EmbeddingAdapter) -> None:
        self._adapter: EmbeddingAdapter = embedding_adapter
        self._records: list[dict[str, Any]] = []
        self._embeddings: list[list[float]] = []

    # ── VectorStore interface ─────────────────────────────────────────────

    def add(self, record: dict[str, Any]) -> None:
        query_text = record.get("query", "")
        self._records.append(record)
        self._embeddings.append(self._adapter.embed(query_text).vector)

    def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7,
    ) -> list[dict[str, Any]]:
        if not self._records:
            return []
        q_vec = self._adapter.embed(query).vector
        scored: list[tuple[int, float]] = []
        for i, rec_vec in enumerate(self._embeddings):
            sim = _cosine_similarity(q_vec, rec_vec)
            if sim >= threshold:
                scored.append((i, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, sim in scored[:top_k]:
            item = dict(self._records[idx])
            item["similarity_score"] = sim
            results.append(item)
        return results

    def persist(self, path: str) -> None:
        data = {
            "model_name": self._adapter.model_name,
            "records": self._records,
            "embeddings": self._embeddings,
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    @classmethod
    def load(
        cls,
        path: str,
        embedding_adapter: EmbeddingAdapter,
    ) -> InMemoryVectorStore:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        store = cls(embedding_adapter)
        store._records = data.get("records", [])
        store._embeddings = data.get("embeddings", [])
        return store

    def __len__(self) -> int:
        return len(self._records)

    def get_statistics(self) -> dict[str, Any]:
        """Return diagnostic statistics."""
        return {
            "total_records": len(self._records),
            "embedding_model": self._adapter.model_name,
            "embedding_dim": len(self._embeddings[0]) if self._embeddings else 0,
            "cache_size": len(self._adapter._cache),
        }


# ─────────────────────────────────────────────────────────────────────────────
# ChromaVectorStore — persistent, requires ``pip install chromadb``
# ─────────────────────────────────────────────────────────────────────────────


class ChromaVectorStore(VectorStore):
    """ChromaDB-backed persistent vector store.

    **Requires**: ``pip install chromadb``

    Args:
        embedding_adapter: Used for query embedding (not for indexing —
            Chroma handles its own embeddings internally).
        path:              Persist directory.  ``None`` = ephemeral in-memory.
        collection_name:   Chroma collection name (default ``"theos_wisdom"``).

    Raises:
        ImportError: If ``chromadb`` is not installed.
    """

    def __init__(
        self,
        embedding_adapter: EmbeddingAdapter,
        path: str | None = None,
        collection_name: str = "theos_wisdom",
    ) -> None:
        try:
            import chromadb  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "ChromaVectorStore requires chromadb.\n" "Install it with:  pip install chromadb"
            ) from exc

        self._adapter = embedding_adapter
        self._collection_name = collection_name
        if path:
            self._client = chromadb.PersistentClient(path=path)
        else:
            self._client = chromadb.Client()
        self._col = self._client.get_or_create_collection(collection_name)
        self._next_id = 0

    def add(self, record: dict[str, Any]) -> None:
        import chromadb  # type: ignore[import]  # noqa: F401

        doc_id = str(self._next_id)
        self._next_id += 1
        self._col.add(
            ids=[doc_id],
            documents=[record.get("query", "")],
            metadatas=[{k: str(v) for k, v in record.items()}],
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7,
    ) -> list[dict[str, Any]]:
        results = self._col.query(query_texts=[query], n_results=top_k)
        out = []
        for meta in (results.get("metadatas") or [[]])[0]:
            out.append(dict(meta))
        return out

    def persist(self, path: str) -> None:
        # ChromaDB PersistentClient auto-persists; this is a no-op.
        pass

    @classmethod
    def load(
        cls,
        path: str,
        embedding_adapter: EmbeddingAdapter,
    ) -> ChromaVectorStore:
        return cls(embedding_adapter, path=path)

    def __len__(self) -> int:
        return int(self._col.count())


# ─────────────────────────────────────────────────────────────────────────────
# FAISSVectorStore — high-performance, requires ``pip install faiss-cpu``
# ─────────────────────────────────────────────────────────────────────────────


class FAISSVectorStore(VectorStore):
    """FAISS-backed vector store for high-throughput semantic search.

    **Requires**: ``pip install faiss-cpu``  (or ``faiss-gpu`` on CUDA)

    Suitable for wisdom stores with > 100 k records.  Uses an ``IndexFlatIP``
    (inner-product / cosine on normalised vectors).

    Args:
        embedding_adapter: Provides the dense vectors.
        dimension:         Embedding dimensionality (must match adapter output).

    Raises:
        ImportError: If ``faiss`` is not installed.
    """

    def __init__(
        self,
        embedding_adapter: EmbeddingAdapter,
        dimension: int = 384,
    ) -> None:
        try:
            import faiss  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "FAISSVectorStore requires faiss.\n" "Install it with:  pip install faiss-cpu"
            ) from exc

        import faiss  # type: ignore[import]  # noqa: F811 (needed for local ref)

        self._adapter = embedding_adapter
        self._dimension = dimension
        self._index = faiss.IndexFlatIP(dimension)
        self._records: list[dict[str, Any]] = []

    def add(self, record: dict[str, Any]) -> None:
        import numpy as np  # type: ignore[import]

        vec = self._adapter.embed(record.get("query", "")).vector
        arr = np.array([vec], dtype="float32")
        self._index.add(arr)
        self._records.append(record)

    def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7,
    ) -> list[dict[str, Any]]:
        import numpy as np  # type: ignore[import]

        if not self._records:
            return []
        vec = self._adapter.embed(query).vector
        arr = np.array([vec], dtype="float32")
        distances, indices = self._index.search(arr, min(top_k, len(self._records)))
        out = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or dist < threshold:
                continue
            item = dict(self._records[idx])
            item["similarity_score"] = float(dist)
            out.append(item)
        return out

    def persist(self, path: str) -> None:
        import pickle

        import faiss  # type: ignore[import]

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        faiss.write_index(self._index, path + ".faiss")
        with open(path + ".records.pkl", "wb") as fh:
            pickle.dump(self._records, fh)

    @classmethod
    def load(
        cls,
        path: str,
        embedding_adapter: EmbeddingAdapter,
    ) -> FAISSVectorStore:
        import pickle

        import faiss  # type: ignore[import]

        dim = embedding_adapter.embed("probe").dimension
        store = cls(embedding_adapter, dimension=dim)
        store._index = faiss.read_index(path + ".faiss")
        with open(path + ".records.pkl", "rb") as fh:
            store._records = pickle.load(fh)
        return store

    def __len__(self) -> int:
        return len(self._records)


# ─────────────────────────────────────────────────────────────────────────────
# SemanticRetrieval — legacy high-level wrapper (kept for compatibility)
# ─────────────────────────────────────────────────────────────────────────────


class SemanticRetrieval:
    """High-level semantic retrieval backed by :class:`InMemoryVectorStore`.

    .. deprecated::
        Prefer :class:`InMemoryVectorStore` (or another :class:`VectorStore`)
        directly.  This class is kept for backward compatibility.
    """

    def __init__(self, embedding_adapter: EmbeddingAdapter) -> None:
        self._store = InMemoryVectorStore(embedding_adapter)
        # expose for legacy callers that poke at internals
        self.embedding_adapter = embedding_adapter
        self.wisdom_records = self._store._records
        self.embeddings = self._store._embeddings

    def add_record(self, record: dict[str, Any]) -> None:
        self._store.add(record)

    def retrieve_similar(
        self,
        query: str,
        threshold: float = 0.7,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        return self._store.search(query, top_k=top_k, threshold=threshold)

    def get_statistics(self) -> dict[str, Any]:
        return self._store.get_statistics()


# ─────────────────────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────────────────────


def get_vector_store(
    backend: str = "memory",
    embedding_adapter: EmbeddingAdapter | None = None,
    path: str | None = None,
    dimension: int = 384,
    **kwargs: Any,
) -> VectorStore:
    """Factory: return a :class:`VectorStore` for the requested *backend*.

    Args:
        backend:           ``"memory"`` | ``"chroma"`` | ``"faiss"``.
        embedding_adapter: Defaults to :class:`MockEmbeddingAdapter` when omitted.
        path:              Persistence path (required for ``"chroma"`` and
                           ``"faiss"`` if loading an existing store).
        dimension:         Vector dimensionality for FAISS.
        **kwargs:          Passed to the backend constructor.

    Returns:
        A ready-to-use :class:`VectorStore` instance.

    Raises:
        ValueError:   Unknown *backend* name.
        ImportError:  Backend dependencies not installed.
    """
    adapter = embedding_adapter or MockEmbeddingAdapter(dimension=dimension)

    if backend == "memory":
        return InMemoryVectorStore(adapter)
    if backend == "chroma":
        return ChromaVectorStore(adapter, path=path, **kwargs)
    if backend == "faiss":
        return FAISSVectorStore(adapter, dimension=dimension, **kwargs)

    raise ValueError(
        f"Unknown vector store backend {backend!r}. " "Choose from: 'memory', 'chroma', 'faiss'."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Utility: cosine similarity
# ─────────────────────────────────────────────────────────────────────────────


def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Cosine similarity mapped to [0, 1]."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have the same dimension")
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return (dot / (mag1 * mag2) + 1.0) / 2.0  # map [-1,1] → [0,1]


# ─────────────────────────────────────────────────────────────────────────────
# Module self-test
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== VectorStore demo ===\n")

    store = get_vector_store("memory", dimension=64)
    records = [
        {
            "query": "What is the relationship between freedom and responsibility?",
            "resolution": "Freedom and responsibility are interdependent.",
            "confidence": 0.85,
        },
        {
            "query": "How should AI systems handle ethical dilemmas?",
            "resolution": "Use multi-perspective reasoning.",
            "confidence": 0.80,
        },
        {
            "query": "What makes a good decision?",
            "resolution": "Balance values, consider long-term consequences.",
            "confidence": 0.82,
        },
    ]
    for r in records:
        store.add(r)

    test_query = "What is the connection between liberty and accountability?"
    print(f"Query: {test_query}\n")
    for i, r in enumerate(store.search(test_query, threshold=0.5, top_k=3), 1):
        print(f"  {i}. [{r['similarity_score']:.2f}] {r['query']}")

    print(f"\nStore: {store}")
    print(f"Stats: {store.get_statistics()}")
