# Document RAG: Chat & Report Generator

A **Retrieval-Augmented Generation (RAG)** system that lets you upload PDFs, ask questions over the content, and generate structured long-form reports—all grounded in your documents.

This is a portfolio project: end-to-end pipeline with clear trade-offs and production-relevant choices (chunking, vector search, citation-aware generation).

## What it does

1. **Upload PDFs** → Extract text, chunk with overlap, embed, store in a vector DB (Chroma).
2. **Chat** → Your question is embedded; relevant chunks are retrieved and passed to an LLM for an answer with source grounding.
3. **Generate report** → You give a topic; the system retrieves broad context and produces a structured Markdown report (table of contents, sections, citations).

## Tech stack

| Component      | Choice           | Why |
|----------------|------------------|-----|
| PDF            | pypdf            | Simple, reliable extraction |
| Chunking       | 800 chars, 150 overlap | Balance retrieval precision vs. context continuity |
| Embeddings     | OpenAI `text-embedding-3-small` | Quality and consistency |
| Vector store   | Chroma (local)   | No signup, good for portfolio/demo |
| LLM            | OpenAI (e.g. `gpt-4o-mini`) | Ease of use; swap for others if needed |
| UI             | Streamlit        | Fast to build and run |

## Setup

1. **Clone and enter the project**
   ```bash
   cd doc-rag-portfolio
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   ```

3. **Configure API key**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key: `OPENAI_API_KEY=sk-...`

4. **Run the app (from project root)**
   ```bash
   streamlit run app/main.py
   ```

5. In the app: upload one or more PDFs → click **Index PDFs** → use **Chat** or **Generate report**.

## Project layout

```
doc-rag-portfolio/
  app/
    main.py          # Streamlit UI
    pdf_processor.py # PDF text extraction + chunking
    vector_store.py  # Chroma + OpenAI embeddings
    rag.py           # Retrieve + format context, Q&A
    generator.py     # Long-form report generation
  config.py         # Chunk size, top_k, model, paths
  data/             # Created at runtime: uploads/, chroma_db/
  README.md
  CUSTOMERS_AND_USE_CASES.md
```

## Design choices (for interviews)

- **Chunk size (800) / overlap (150)**  
  Smaller chunks improve retrieval precision; overlap reduces boundary cuts. You can tune these in `config.py`.

- **Why Chroma?**  
  Local and free for a portfolio; easy to swap to pgvector or Pinecone for “how would you scale?” discussions.

- **Why cite sources?**  
  Report prompt asks the model to output [1], [2] corresponding to retrieved chunks—shows you care about traceability and hallucination control.

- **Report length (~2k words)**  
  Enough to demonstrate “document-grounded long-form” without the cost and complexity of 20k-word runs.

## Resume-style one-liner

**Designed and implemented a Retrieval-Augmented Generation (RAG) system for document-grounded Q&A and long-form report generation, including chunking strategy, vector search (Chroma), and citation-aware LLM output.**

## License

Use and adapt for your portfolio. No warranty.
