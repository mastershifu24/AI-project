"""
Long-form report generation from retrieved context.
Retrieval uses local embeddings (free). Only the LLM call uses OpenAI.
"""
from openai import OpenAI

from config import TOP_K, TARGET_REPORT_WORDS, MAX_REPORT_SECTIONS, OPENAI_CHAT_MODEL
from app.vector_store import DocVectorStore
from app.rag import build_context


def _retrieve_for_report(store: DocVectorStore, topic: str) -> str:
    """Retrieve more context for report (broader + higher top_k)."""
    chunks = store.query(topic, top_k=min(TOP_K * 2, 20))
    return build_context(chunks)


def generate_report(
    store: DocVectorStore,
    openai_client: OpenAI,
    topic: str,
    model: str = OPENAI_CHAT_MODEL,
    target_words: int = TARGET_REPORT_WORDS,
    max_sections: int = MAX_REPORT_SECTIONS,
) -> str:
    """
    Generate a structured report (table of contents, sections, citations) from document context.
    """
    context = _retrieve_for_report(store, topic)

    system = """You are an expert technical writer. You write clear, structured reports based only on the provided document context. You must:
- Use only information from the context; cite source numbers like [1], [2] when referring to the numbered sources.
- Output well-structured Markdown: title, table of contents, then sections with ## and ### headings.
- Be concise but substantive; aim for the requested word count.
- Do not invent information not present in the context."""

    user = f"""Document context:\n\n{context}\n\n---\n\nWrite a structured report on the following topic, using only the context above. Use Markdown headings (## and ###), a table of contents at the top, and cite sources as [1], [2], etc.\n\nTopic: {topic}\n\nTarget length: approximately {target_words} words. Use at most {max_sections} main sections. Write the full report now."""

    response = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content or ""
