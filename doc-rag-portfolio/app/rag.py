"""
RAG: retrieve relevant chunks and format context for the LLM.
"""
from openai import OpenAI

from config import TOP_K
from app.vector_store import DocVectorStore


def build_context(chunks: list[tuple[str, dict]], separator: str = "\n\n---\n\n") -> str:
    """Format retrieved chunks into a single context string with source labels."""
    parts = []
    for i, (doc, meta) in enumerate(chunks, 1):
        source = meta.get("source", "document")
        parts.append(f"[{i}] (Source: {source})\n{doc}")
    return separator.join(parts)


def retrieve_and_build_context(
    store: DocVectorStore,
    openai_client: OpenAI,
    query: str,
    top_k: int = TOP_K,
) -> str:
    """Retrieve top_k chunks for query and return formatted context."""
    chunks = store.query(query, openai_client, top_k=top_k)
    return build_context(chunks)


def answer_with_rag(
    store: DocVectorStore,
    openai_client: OpenAI,
    query: str,
    model: str,
    system_prompt: str | None = None,
) -> str:
    """
    RAG-based Q&A: retrieve context, then generate answer.
    """
    context = retrieve_and_build_context(store, openai_client, query)
    default_system = """You are a helpful assistant. Answer based ONLY on the provided context. If the context does not contain enough information, say so. Do not make up facts."""
    system = system_prompt or default_system
    user = f"""Context from documents:\n\n{context}\n\nQuestion: {query}\n\nAnswer (based only on the context above):"""

    resp = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content or ""
