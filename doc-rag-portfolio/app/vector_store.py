"""
Vector store using Chroma (local, no API for embeddings storage).
Embeddings via OpenAI for quality and consistency with typical production stacks.
"""
from pathlib import Path
import uuid

import chromadb
from chromadb.config import Settings
from openai import OpenAI

from config import CHROMA_DIR, OPENAI_EMBEDDING_MODEL


def get_embedding(client: OpenAI, text: str, model: str = OPENAI_EMBEDDING_MODEL) -> list[float]:
    """Single text to embedding."""
    resp = client.embeddings.create(input=[text], model=model)
    return resp.data[0].embedding


def get_embeddings_batch(client: OpenAI, texts: list[str], model: str = OPENAI_EMBEDDING_MODEL) -> list[list[float]]:
    """Batch embed (OpenAI allows batch)."""
    if not texts:
        return []
    resp = client.embeddings.create(input=texts, model=model)
    # Preserve order by index
    by_idx = {d.index: d.embedding for d in resp.data}
    return [by_idx[i] for i in range(len(texts))]


class DocVectorStore:
    """Chroma-backed store for document chunks with OpenAI embeddings."""

    def __init__(self, persist_dir: Path = CHROMA_DIR, collection_name: str = "doc_rag"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection_name = collection_name
        self._collection = None
        self._openai = None

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Document chunks for RAG"},
            )
        return self._collection

    def set_openai_client(self, client: OpenAI):
        self._openai = client

    def add_chunks(self, chunks: list[tuple[str, dict]], openai_client: OpenAI):
        """Add chunks with metadata. Embeds via OpenAI."""
        if not chunks:
            return
        texts = [c[0] for c in chunks]
        metadatas = [c[1] for c in chunks]
        # Chroma expects str values in metadata
        for m in metadatas:
            for k, v in m.items():
                if not isinstance(v, (str, int, float, bool)):
                    m[k] = str(v)

        embeddings = get_embeddings_batch(openai_client, texts)
        ids = [str(uuid.uuid4()) for _ in chunks]
        self.collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

    def query(self, query_text: str, openai_client: OpenAI, top_k: int = 8) -> list[tuple[str, dict]]:
        """Return top_k (document, metadata) for query."""
        q_embedding = get_embedding(openai_client, query_text)
        results = self.collection.query(
            query_embeddings=[q_embedding],
            n_results=top_k,
            include=["documents", "metadatas"],
        )
        docs = results["documents"][0] if results["documents"] else []
        metas = results["metadatas"][0] if results["metadatas"] else []
        return list(zip(docs, metas))

    def clear(self):
        """Remove all documents in the collection (for re-indexing)."""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass  # Collection doesn't exist yet — nothing to clear
        self._collection = None
