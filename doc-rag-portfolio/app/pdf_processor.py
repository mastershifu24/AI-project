"""
PDF ingestion and chunking.
Chunk size and overlap are tuned for retrieval quality vs. context continuity.
"""
from pathlib import Path
from typing import Iterator

from pypdf import PdfReader

# Run from project root so config is importable
from config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_text_from_pdf(path: Path) -> str:
    """Extract raw text from a PDF file."""
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n\n".join(parts)


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> Iterator[tuple[str, dict]]:
    """
    Split text into overlapping chunks with metadata.
    Yields (chunk_text, metadata) for each chunk.
    """
    text = text.strip()
    if not text:
        return

    start = 0
    chunk_id = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if not chunk.strip():
            start = end - overlap
            continue

        # Prefer breaking on paragraph or sentence
        if end < len(text):
            for sep in ["\n\n", "\n", ". "]:
                last_sep = chunk.rfind(sep)
                if last_sep > chunk_size // 2:
                    chunk = chunk[: last_sep + len(sep)].strip()
                    end = start + len(chunk)
                    break

        yield chunk, {"chunk_id": chunk_id, "start": start, "end": end}
        chunk_id += 1
        start = end - overlap


def process_pdf(path: Path) -> list[tuple[str, dict]]:
    """
    Load a PDF and return list of (chunk_text, metadata).
    Metadata includes chunk_id and optional source filename.
    """
    text = extract_text_from_pdf(path)
    meta_base = {"source": path.name}
    return [
        (chunk, {**meta_base, **m})
        for chunk, m in chunk_text(text)
    ]


def process_pdfs(paths: list[Path]) -> list[tuple[str, dict]]:
    """Process multiple PDFs and return combined chunks with source in metadata."""
    all_chunks = []
    for path in paths:
        all_chunks.extend(process_pdf(path))
    return all_chunks
