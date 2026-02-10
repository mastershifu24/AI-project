"""
Configuration for the RAG pipeline.
Tunable knobs that affect retrieval quality and cost.
"""
import os
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).resolve().parent / "data"
CHROMA_DIR = DATA_DIR / "chroma_db"
UPLOADS_DIR = DATA_DIR / "uploads"

# PDF chunking (trade-off: smaller = more precise retrieval, more chunks = higher cost)
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Retrieval
TOP_K = 8
MIN_RELEVANCE = 0.0  # Optional: filter by similarity score

# Generation
MAX_REPORT_SECTIONS = 8
TARGET_REPORT_WORDS = 2000  # Portfolio version: 2k words is plenty to show capability
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

# Local embedding model (free, no API key needed)
LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
