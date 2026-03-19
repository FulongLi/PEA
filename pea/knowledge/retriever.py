"""
RAG retriever for power electronics knowledge base.
"""

from __future__ import annotations

import os
from pathlib import Path

from pea.knowledge.documents import KNOWLEDGE_DOCUMENTS


class KnowledgeRetriever:
    """
    Retrieves relevant power electronics knowledge for RAG.
    Uses ChromaDB for vector storage when available, falls back to simple keyword search.
    """

    def __init__(self, use_vector_store: bool = True, persist_dir: str | None = None):
        self.use_vector_store = use_vector_store
        self.persist_dir = persist_dir or str(Path.home() / ".pea" / "chroma_db")
        self._vector_store = None
        self._embeddings = None

        if use_vector_store:
            self._init_vector_store()

    def _init_vector_store(self) -> None:
        """Initialize ChromaDB vector store with knowledge documents."""
        try:
            import chromadb
            from chromadb.config import Settings
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

            # Local embedding, no API key needed
            ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
            client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=Settings(anonymized_telemetry=False),
            )
            collection = client.get_or_create_collection(
                name="pea_knowledge",
                embedding_function=ef,
                metadata={"description": "Power electronics knowledge"},
            )

            # Add documents if collection is empty
            if collection.count() == 0:
                ids = [doc["id"] for doc in KNOWLEDGE_DOCUMENTS]
                documents = [doc["content"].strip() for doc in KNOWLEDGE_DOCUMENTS]
                metadatas = [doc["metadata"] for doc in KNOWLEDGE_DOCUMENTS]
                collection.add(ids=ids, documents=documents, metadatas=metadatas)

            self._vector_store = collection
            self._embeddings = ef

        except ImportError:
            self.use_vector_store = False
            self._vector_store = None

    def search(self, query: str, top_k: int = 4) -> list[str]:
        """
        Search knowledge base for relevant content.

        Args:
            query: User question or search term
            top_k: Number of results to return

        Returns:
            List of relevant document content strings
        """
        if self._vector_store is not None:
            results = self._vector_store.query(
                query_texts=[query],
                n_results=min(top_k, len(KNOWLEDGE_DOCUMENTS)),
            )
            if results and results["documents"] and results["documents"][0]:
                return results["documents"][0]
            return []

        # Fallback: simple keyword matching
        query_lower = query.lower()
        scored = []
        keywords = set(query_lower.split())

        for doc in KNOWLEDGE_DOCUMENTS:
            content_lower = doc["content"].lower()
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                scored.append((score, doc["content"]))

        scored.sort(key=lambda x: -x[0])
        return [content for _, content in scored[:top_k]]
