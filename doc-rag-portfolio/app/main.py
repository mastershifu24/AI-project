"""
Streamlit UI: PDF upload, RAG chat, and long-form report generation.
Run from project root: streamlit run app/main.py
"""
import os
import sys
from pathlib import Path

# Ensure project root is on path when running as streamlit run app/main.py
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from config import (
    CHROMA_DIR,
    UPLOADS_DIR,
    OPENAI_CHAT_MODEL,
    TARGET_REPORT_WORDS,
)
from app.pdf_processor import process_pdfs
from app.vector_store import DocVectorStore
from app.rag import answer_with_rag
from app.generator import generate_report

load_dotenv()


def ensure_dirs():
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)


def get_openai():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        st.error("Set OPENAI_API_KEY in .env (see .env.example).")
        return None
    return OpenAI(api_key=key)


def main():
    ensure_dirs()
    st.set_page_config(page_title="Doc RAG — Chat & Report", layout="wide")
    st.title("Document RAG: Chat & Report Generator")
    st.caption("Upload PDFs, ask questions, or generate a structured report from your documents.")

    openai_client = get_openai()
    if not openai_client:
        st.stop()

    store = DocVectorStore()

    # Sidebar: upload and index
    with st.sidebar:
        st.header("Documents")
        uploaded = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)
        if uploaded:
            for f in uploaded:
                path = UPLOADS_DIR / f.name
                path.write_bytes(f.getvalue())
            st.success(f"Saved {len(uploaded)} file(s). Click 'Index PDFs' to add to the knowledge base.")

        if st.button("Index PDFs"):
            paths = list(UPLOADS_DIR.glob("*.pdf"))
            if not paths:
                st.warning("No PDFs in uploads. Upload files first.")
            else:
                with st.spinner("Chunking and embedding..."):
                    store.clear()
                    chunks = process_pdfs(paths)
                    store.add_chunks(chunks, openai_client)
                st.success(f"Indexed {len(chunks)} chunks from {len(paths)} PDF(s).")

        if st.button("Clear index"):
            store.clear()
            st.info("Index cleared. Upload and index again to re-add documents.")

    # Main area: mode and content
    mode = st.radio("Mode", ["Chat (Q&A)", "Generate report"], horizontal=True)

    if mode == "Chat (Q&A)":
        q = st.chat_input("Ask something about your documents...")
        if q:
            with st.chat_message("user"):
                st.write(q)
            with st.chat_message("assistant"):
                with st.spinner("Retrieving and answering..."):
                    answer = answer_with_rag(store, openai_client, q, OPENAI_CHAT_MODEL)
                st.markdown(answer)

    else:
        topic = st.text_input(
            "Report topic",
            placeholder="e.g. Create a handbook on Retrieval-Augmented Generation",
            key="report_topic",
        )
        if st.button("Generate report"):
            if not topic:
                st.warning("Enter a topic.")
            else:
                with st.spinner("Retrieving context and generating report (this may take a minute)..."):
                    report = generate_report(
                        store,
                        openai_client,
                        topic,
                        model=OPENAI_CHAT_MODEL,
                        target_words=TARGET_REPORT_WORDS,
                    )
                st.markdown(report)
                st.download_button(
                    "Download as Markdown",
                    data=report,
                    file_name="report.md",
                    mime="text/markdown",
                )


if __name__ == "__main__":
    main()
