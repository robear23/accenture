"""ChromaDB persistent retriever for the knowledge base."""

from __future__ import annotations

import chromadb

from job_assistant.config import CHROMA_DB_DIR, settings
from job_assistant.rag.embeddings import get_embedding_function
from job_assistant.rag.knowledge_base import load_knowledge_base
from job_assistant.utils.logger import get_logger

logger = get_logger(__name__)

_client: chromadb.PersistentClient | None = None
_embedding_fn = None


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    return _client


def _get_embedding_fn():
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = get_embedding_function()
    return _embedding_fn


def index_knowledge_base(force: bool = False) -> int:
    """Index all knowledge base chunks into ChromaDB.

    Args:
        force: If True, delete existing collection and re-index.

    Returns:
        Number of chunks indexed.
    """
    client = _get_client()
    ef = _get_embedding_fn()

    # Check if collection exists and has data
    try:
        collection = client.get_collection(
            name=settings.chroma_collection,
            embedding_function=ef,
        )
        if collection.count() > 0 and not force:
            logger.info(
                f"Collection '{settings.chroma_collection}' already has "
                f"{collection.count()} documents. Use --reindex to force."
            )
            return collection.count()
        # Force re-index: delete and recreate
        client.delete_collection(settings.chroma_collection)
    except Exception:
        pass  # Collection doesn't exist yet

    collection = client.get_or_create_collection(
        name=settings.chroma_collection,
        embedding_function=ef,
    )

    chunks = load_knowledge_base()
    if not chunks:
        logger.warning("No chunks to index.")
        return 0

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    logger.info(f"Indexed {len(chunks)} chunks into ChromaDB.")
    return len(chunks)


def retrieve(query: str, top_k: int | None = None) -> list[dict]:
    """Retrieve relevant chunks for a single query.

    Returns list of dicts with keys: text, metadata, distance.
    """
    k = top_k or settings.rag_top_k
    client = _get_client()
    ef = _get_embedding_fn()

    collection = client.get_collection(
        name=settings.chroma_collection,
        embedding_function=ef,
    )

    results = collection.query(query_texts=[query], n_results=k)

    retrieved = []
    for i in range(len(results["ids"][0])):
        retrieved.append({
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })
    return retrieved


def multi_query_retrieve(queries: list[str], top_k: int | None = None) -> list[dict]:
    """Retrieve relevant chunks for multiple queries, deduplicated.

    Builds one query per job requirement for comprehensive RAG coverage.
    Returns deduplicated list of chunks sorted by best (lowest) distance.
    """
    seen_texts: set[str] = set()
    all_results: list[dict] = []

    for query in queries:
        results = retrieve(query, top_k=top_k)
        for r in results:
            if r["text"] not in seen_texts:
                seen_texts.add(r["text"])
                all_results.append(r)

    # Sort by distance (lower = more relevant)
    all_results.sort(key=lambda x: x["distance"])
    return all_results
