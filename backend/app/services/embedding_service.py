"""
Embedding Service - DISABLED.
HR RAG/policy search telah dibuang dari scope.
File ini dikekalkan sebagai stub untuk compatibility.
"""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Stub - Embedding service disabled (HR RAG out of scope)."""

    async def get_embeddings(self, text: str) -> List[float]:
        logger.warning("⚠️ Embedding service disabled - HR RAG out of scope")
        return []

    async def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        logger.warning("⚠️ Batch embedding disabled")
        return []


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get embedding service singleton."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
