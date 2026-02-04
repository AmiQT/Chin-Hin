"""
Embedding Service for Knowledge Base.
Uses Gemini Embeddings to convert text into vectors.
"""

import logging
from typing import List, Optional
from google import genai
from app.config import get_settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service to handle text embeddings using Gemini."""
    
    def __init__(self):
        self._client: Optional[genai.Client] = None
        self.model = "text-embedding-004"  # Latest Google embedding model
    
    def _get_client(self) -> Optional[genai.Client]:
        """Get or create Gemini client."""
        if self._client is not None:
            return self._client
        
        settings = get_settings()
        api_keys = settings.gemini_api_key_list
        if not api_keys:
            logger.warning("⚠️ No Gemini API keys configured for Embeddings!")
            return None
        
        try:
            self._client = genai.Client(api_key=api_keys[0])
            return self._client
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {e}")
            return None
    
    async def get_embeddings(self, text: str) -> List[float]:
        """Convert text to embedding vector."""
        client = self._get_client()
        if not client:
            return []
            
        try:
            response = client.models.embed_content(
                model=self.model,
                contents=text,
                config={
                    "output_dimensionality": 768  # Solid balance between speed & quality
                }
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"❌ Embedding error: {e}")
            return []

    async def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Convert multiple texts to embedding vectors."""
        client = self._get_client()
        if not client:
            return []
            
        try:
            response = client.models.embed_content(
                model=self.model,
                contents=texts,
                config={
                    "output_dimensionality": 768
                }
            )
            return [e.values for e in response.embeddings]
        except Exception as e:
            logger.error(f"❌ Batch embedding error: {e}")
            return []

# Singleton instance
_embedding_service: Optional[EmbeddingService] = None

def get_embedding_service() -> EmbeddingService:
    """Get embedding service singleton."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
