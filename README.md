# <img src="https://raw.githubusercontent.com/user-attachments/assets/logo_placeholder.png" width="48" /> Universal Vectorizer
**Enterprise-grade RAG ingestion engine** for large PDFs, CSVs, JSON, OCR, audio, and unstructured data — built for modern LLM pipelines, vector databases, and high-throughput semantic search applications.

**Created by _Vibhanshu Kumar Shubham_ — DevOps & AI Engineer**

---

<p align="center">
  <img src="https://raw.githubusercontent.com/user-attachments/assets/banner_placeholder.png" width="100%" />
</p>

<p align="center">
  <img alt="GitHub Stars" src="https://img.shields.io/github/stars/Theubaa/universal-vectorizer?style=for-the-badge">
  <img alt="Issues" src="https://img.shields.io/github/issues/Theubaa/universal-vectorizer?style=for-the-badge">
  <img alt="Forks" src="https://img.shields.io/github/forks/Theubaa/universal-vectorizer?style=for-the-badge">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge">
</p>

---

# 🚀 Overview

**Universal Vectorizer** is a **production-grade ingestion + embedding engine** that turns chaotic enterprise files into clean, searchable vector embeddings.

It handles:

- **PDFs (single or multi-gigabyte)**
- **CSV / Excel dumps**
- **Massive JSON / NDJSON logs**
- **Images → OCR text**
- **Audio → Whisper transcription**
- **Web URLs**
- **Binary formats (custom handlers)**

Built for users searching:
`universal vectorizer, rag pipeline, llm ingestion, openai embeddings streaming, enterprise vector search, multimodal ingestion, pdf ocr, qdrant, pinecone, chroma`.

---

# ⚡ Pipeline at a Glance

```mermaid
flowchart LR
    A[Client Upload / URL] --> B[Streaming Ingestion Service]
    B --> C[Preprocessor (OCR / Parsing)]
    C --> D[Streaming Hybrid Chunker]
    D --> E[Batched Async Embeddings (OpenAI + HF Fallback)]
    E --> F[Vector DB Layer (Chroma / Pinecone / Qdrant)]
    F --> G[Semantic Search API & Dashboard]


🧩 Step-by-Step System Story (Screenshots Included)
1️⃣ Upload Anything (PDF, CSV, JSON, Audio, Images)

Multi-gigabyte files stream safely with backpressure.

<img width="100%" src="https://github.com/user-attachments/assets/547a1e26-c7ac-47a9-97e6-63c3013727ca" /> <img width="100%" src="https://github.com/user-attachments/assets/62b6aa61-9924-4a96-b2b5-9654e39ef0fd" /> <img width="100%" src="https://github.com/user-attachments/assets/a8358eea-ea6b-435d-8734-1de249e032c4" />
2️⃣ Streaming Extraction

PDF → page iterator

CSV → row iterator

JSON → incremental ijson parser

Audio → Whisper chunks

OCR → Tesseract

🧠 Zero memory blowups — never loads entire file at once

3️⃣ Cleaning & Normalization

Noise removal, whitespace normalization, semantic-safe text blocks.

4️⃣ Smart Streaming Chunker

Hybrid window + semantic chunking.
Optimized for LLM context fidelity.

5️⃣ Async Embedding Engine

OpenAI async batching

HuggingFace Instructor-large, MiniLM fallback

Retry/backoff

Rate-limit control

GPU-ready

6️⃣ Vector DB Persistence

Supported providers:

🟦 Chroma

🟧 Pinecone

🟥 Qdrant

Batching + idempotent inserts + metadata guarantees.

7️⃣ Semantic Search UI

FastAPI backend + React dashboard:

Job progress

Real-time WS logs

Chunk stats

Vector DB metrics

Search with snippets

Metadata viewer

📂 Repository Structure
backend/
  app/
    main.py
    config.py
    logger.py
    core/
      progress.py
      checkpoint.py
    routes/
    services/
    pipelines/
      ingestion_pipeline.py
    utils/
      ingestion/
      preprocess/
      chunking/
      embeddings/
      vectordb/
      json_flattener.py
      file_utils.py

frontend/
  src/
    pages/
    components/
    services/api.js
    styles/global.css

Backend Setup
cd backend
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
copy NUL .env
notepad .env
uvicorn app.main:app --reload

| Key                  | Purpose                      |
| -------------------- | ---------------------------- |
| OPENAI_API_KEY       | Needed for OpenAI embeddings |
| EMBEDDING_BACKEND    | openai / huggingface         |
| HF_MODEL_NAME        | Instructor-xl / MiniLM       |
| VECTORDB_PROVIDER    | chroma / pinecone / qdrant   |
| QDRANT_URL           | Vector DB endpoint           |
| PINECONE_API_KEY     | Pinecone                     |
| CHUNK_BATCH_SIZE     | Controls throughput          |
| EMBEDDING_BATCH_SIZE | OpenAI or HF batching        |


🎨 Frontend Setup
cd frontend
npm install
npm run dev


Optional .env:

VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

🔌 API Surface
Upload & Ingest

POST /upload

POST /ingest

Job Status

GET /ingest/jobs

GET /ingest/{id}/status

WS /ws/ingest/{id}

Search

POST /search

🧪 Load Testing Guide

10GB CSV stress test

20GB PDF OCR test

50GB–100GB ingestion stress

Concurrency via Locust/k6

Embedding cosine validation

Vector DB cleanup & audit

🛡 Production Checklist

Structured logging

Prometheus/FastAPI metrics

Durable vector DB storage

GPU for HuggingFace

Backpressure controls

Error retries + alerting

Horizontal scaling via queue workers

📌 Search Result Contract
{
  "id": "storage/uploads/123-chunk-42",
  "score": 0.12,
  "text": "chunk snippet...",
  "metadata": {
    "source": "storage/uploads/123.pdf",
    "type": "pdf",
    "chunk_index": 42,
    "embedding_model": "text-embedding-3-large"
  }
}

🧱 Extending the Ingestion Engine
from app.utils.ingestion.base import IngestionHandler, StreamedDocument

class CustomBinaryHandler(IngestionHandler):
    supported_types = [".bin"]

    def stream(self, source):
        def iter_chunks():
            with open(source, "rb") as f:
                while chunk := f.read(65536):
                    yield chunk.decode("utf-8", errors="ignore")
        return StreamedDocument(chunks=iter_chunks(), metadata={"type": "binary"})

🤝 Contributing

Contributions welcome!
Open issues, submit PRs, suggest new ingestion handlers or vector DB providers.

📄 License

MIT License — free for commercial and enterprise use.

© 2025 — Created by Vibhanshu Kumar Shubham, DevOps & AI Engineer.

❤️ Final Note

This project was created to help teams build scalable, reliable, enterprise-grade RAG pipelines capable of ingesting anything from simple PDFs to massive 50GB datasets.

