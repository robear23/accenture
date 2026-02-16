"""SentenceTransformer embedding wrapper for ChromaDB."""

from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from job_assistant.config import settings
from job_assistant.utils.logger import get_logger

logger = get_logger(__name__)


def get_embedding_function() -> SentenceTransformerEmbeddingFunction:
    """Get the SentenceTransformer embedding function for ChromaDB."""
    logger.info(f"Loading embedding model: {settings.embedding_model}")
    return SentenceTransformerEmbeddingFunction(
        model_name=settings.embedding_model,
    )
