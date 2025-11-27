# Universal Vectorizer

## What this system is (and who it serves)
Universal Vectorizer is a production-grade, streaming ingestion and semantic search platform for teams that need to index *any* enterprise data—PDFs, text, massive CSV/Excel dumps, terabyte-scale JSON, audio (Whisper), and web pages—without losing fidelity. It normalizes and chunks content in a memory-safe way, generates embeddings with OpenAI or local HuggingFace models, and stores vectors in Chroma, Pinecone, or Qdrant for low-latency retrieval. Data engineers, ML platform teams, knowledge-management squads, and LLM application builders can plug it into existing stacks to create scalable RAG foundations.

## Pipeline at a glance
```mermaid
flowchart LR
    A[Client Upload / URL] --> B[Streaming Ingestion Service]
    B --> C[Preprocessor (OCR/Parsing)]
    C --> D[Streaming Hybrid Chunker]
    D --> E[Batched Async Embeddings<br/>OpenAI + HF fallback]
    E --> F[Vector DB Abstraction<br/>Chroma / Pinecone / Qdrant]
    F --> G[Semantic Search API + UI]
```

## Step-by-step story
1. **Upload anything** – Users drag in multi-gig files or paste URLs. Uploads are streamed to disk using bounded buffers.
2. **Streaming extraction** – Modality-specific handlers (PDF pages, CSV rows, JSON via `ijson`, OCR, Whisper, BeautifulSoup) yield text blocks without loading the entire document into memory.
3. **Cleaning & normalization** – A memory-safe cleaner removes noise, dedupes whitespace, and feeds a streaming chunker.
4. **Smart chunking** – Semantic units are combined with fixed windows to create overlap-aware chunks on the fly.
5. **Async embedding batches** – Chunk batches are sent to OpenAI via the async SDK with retry/backoff; failures automatically fall back to the HuggingFace Instructor/all-MiniLM stack (GPU-capable).
6. **Vector persistence** – Embeddings are written in batches to the configured vector DB with durability, retry logic, and backpressure via semaphores/checkpoints.
7. **Search & analytics** – The FastAPI layer exposes upload/ingest/search endpoints plus job-status feeds (REST + WebSocket). The React dashboard visualizes progress, logs, filters, and paginated search results with metadata modals.

## Repository layout
```
backend/
  app/
    main.py               # FastAPI entrypoint
    config.py             # Tightly typed settings + .env loading
    logger.py             # Rotating structured logs
    core/
      checkpoint.py       # Resume-able ingestion checkpoints
      progress.py         # Job manager + websocket broadcaster
    routes/               # Async REST + websocket endpoints
    services/             # Upload, ingestion orchestration, search
    pipelines/
      ingestion_pipeline.py  # Streaming pipeline w/ batching + retries
    utils/
      ingestion/          # Streaming handlers (pdf/text/json/url/etc.)
      preprocess/         # Cleaners
      chunking/           # Streaming hybrid chunker
      embeddings/         # Async OpenAI + HF backends
      vectordb/           # Chroma, Pinecone, Qdrant drivers
      json_flattener.py   # Infinite-depth flattener (still available)
      file_utils.py       # Memory-safe upload helpers
frontend/
  src/
    pages/                # Upload, Status, Search
    components/           # Dropzone, job table, metadata modal, etc.
    services/api.js       # REST + websocket client helpers
    styles/global.css     # Modern responsive UI
```

## Backend setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy NUL .env
notepad .env                  # add keys (see table below)
uvicorn app.main:app --reload
```

### Key environment variables
| Variable | Purpose |
| --- | --- |
| `OPENAI_API_KEY` | Required for OpenAI embeddings |
| `EMBEDDING_BACKEND` | `openai` (default) or `huggingface` |
| `HF_MODEL_NAME` | HF model (Instructor-large, all-MiniLM, etc.) |
| `VECTORDB_PROVIDER` | `chroma`, `pinecone`, or `qdrant` |
| `PINECONE_API_KEY`, `PINECONE_INDEX`, `PINECONE_ENVIRONMENT` | Needed if Pinecone is selected |
| `QDRANT_URL`, `QDRANT_API_KEY` | Needed if Qdrant is selected |
| `DEFAULT_CHUNK_SIZE`, `DEFAULT_CHUNK_OVERLAP` | Hybrid chunking controls |
| `CHUNK_BATCH_SIZE`, `EMBEDDING_BATCH_SIZE` | Flow-control knobs |
| `INGESTION_CONCURRENCY` | Max concurrent ingestion jobs |
| `ALLOWED_ORIGINS` | CORS settings for the UI |

### Extending ingestion
```python
from app.utils.ingestion.base import IngestionHandler, StreamedDocument
from app.utils.ingestion.registry import registry

class CustomBinaryHandler(IngestionHandler):
    supported_types = [".bin"]

    def stream(self, source: Path) -> StreamedDocument:
        def iter_bytes():
            with source.open("rb") as fh:
                while chunk := fh.read(65536):
                    yield chunk.decode("utf-8", errors="ignore")
        return StreamedDocument(chunks=iter_bytes(), metadata={"source": str(source), "type": "custom"})

registry.register(CustomBinaryHandler.supported_types, CustomBinaryHandler)
```

## Frontend setup
```bash
cd frontend
npm install
npm run dev
```
Optional `.env`:
```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## API surface
- `GET /health` – readiness probe.
- `POST /upload` – streaming multipart upload → `{ file_path, filename }`.
- `POST /ingest` – body `{ file_path?, url?, metadata? }` → `{ job_id }`.
- `GET /ingest/jobs` – list of recent job snapshots.
- `GET /ingest/{job_id}/status` – single job snapshot.
- `WS /ws/ingest/{job_id}` – realtime job telemetry (optional).
- `POST /search` – `{ query, top_k, offset, filters? }` → matches with metadata + snippets.

## Production checklist
- [ ] **Logging** – Ship `storage/logs/app.log` to ELK/Grafana; add trace IDs per job.
- [ ] **Monitoring** – Scrape FastAPI metrics, track chunk throughput, vector DB latency.
- [ ] **Vector DB persistence** – Ensure Chroma path sits on durable disk / mount Pinecone/Qdrant with backups.
- [ ] **Concurrency tests** – Increase `INGESTION_CONCURRENCY` gradually; watch semaphore contention.
- [ ] **Memory-pressure tests** – Feed 50GB text/CSV, verify RSS stays flat thanks to streaming handlers.
- [ ] **OCR + Whisper dependencies** – Install Tesseract binaries + GPU/CUDA drivers where needed.
- [ ] **CPU/GPU sizing** – OpenAI offloads work, but HuggingFace fallback benefits from GPU acceleration.
- [ ] **Horizontal scaling** – Run multiple workers behind a queue (job tracker is process-safe).
- [ ] **Error handling & retries** – Embedding retries/backoff configured; add alerting on repeated fallback usage.

## Load testing & stress testing guide
1. **10GB shakedown** – Use large CSV/JSON; confirm ingestion completes without spikes, checkpoints cleaned up.
2. **20GB PDF batch** – Mixed PDFs to benchmark OCR throughput; monitor Whisper/Tesseract CPU.
3. **50GB–100GB CSV** – Stream via CLI (`split` + upload) or direct drag/drop; verify chunk counts & checkpoints.
4. **Simulate load** – Fire multiple `/ingest` jobs concurrently (e.g., k6, Locust) to validate semaphore limits and job tracking.
5. **Embedding correctness** – Spot-check by querying known strings; ensure embeddings from primary & fallback models align (cosine similarity thresholds).
6. **Vector DB audit** – Query `n` results and ensure metadata/source traces match original input; test batch deletes if needed.

## Limitations & future work
- GPU acceleration for HuggingFace embeddings is supported but not auto-configured—deploy on GPU nodes for best throughput.
- OCR + PDF extraction currently operate page-by-page; for extreme documents, integrate genuine streaming OCR (e.g., pdfminer.six incremental parsing).
- Chunking + checkpoints are single-node; multi-node ingestion would require shared checkpoint stores (Redis/S3) and distributed locks.
- Audio/Whisper ingestion still transcribes whole files before chunking (Whisper API limitation).
- Authentication/multi-tenant RBAC is not included—front the API with your IdP/gateway.

## Search result contract
```json
{
  "id": "storage/uploads/123-chunk-42",
  "score": 0.12,
  "text": "chunk snippet ...",
  "metadata": {
    "source": "storage/uploads/123.pdf",
    "type": "pdf",
    "chunk_index": 42,
    "embedding_model": "text-embedding-3-large",
    "tag": "contracts"
  }
}
```

Use the Upload/Status/Search pages (or REST/WS APIs) end-to-end to verify ingestion, progress tracking, and retrieval quality. Stay within the production checklist to harden deployments for enterprise-grade loads.
