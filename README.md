# AI Engineering Knowledge Assistant

Production-style RAG knowledge base: upload documents, hybrid semantic + keyword search over **PostgreSQL + pgvector**, and grounded answers via **OpenRouter**.

## Quick start (Docker)

```bash
cp .env.example .env
# Set OPENROUTER_API_KEY in .env for real RAG answers

docker compose up --build -d
docker compose exec fastapi_app alembic upgrade head
```

| Service | URL |
|--------|-----|
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| Frontend (dev) | http://localhost:5173 |
| Grafana | http://localhost:3000 (admin/admin) |

## Demo flow

1. Open http://localhost:5173 and **Register** / **Login**.
2. Create a **Knowledge base**.
3. **Documents** tab: upload PDF, TXT, Markdown, or DOCX. Status moves `uploaded` → `parsing` → `indexing` → `completed` (list auto-refreshes while processing).
4. **Ask** tab: question about your upload (requires at least one indexed document). Each answer shows **model**, **tokens**, **estimated cost**, and a **View pipeline** link.
5. **Search** tab: inspect hybrid retrieval scores.
6. **History** tab: past queries with pipeline traces (retrieval → LLM spans).

## Query history and pipeline observability

Each `/v1/rag` call persists a `query_executions` row and nested `pipeline_spans` (hybrid search, LLM gateway, etc.). The UI **History** tab lists past questions; opening a run shows an interactive **pipeline explorer** (Graph / Waterfall / Events / Raw) aligned with GodsEye-Dashboard—click a span node to inspect inputs, outputs, tokens, and routing metadata.

The **LLM gateway auto-routes** between named plugs (`LLM_ROUTING_*` in `.env`) using **semantic similarity** from retrieval (not RRF fusion score), plus question length—no manual model picker in the UI.

## Environment variables

See [.env.example](.env.example). Important keys:

- `DATABASE_URL` — Postgres (default matches `docker-compose.yml`)
- `LOCAL_STORAGE_DIR` — uploaded file blobs (Docker volume `document_storage`)
- `EMBEDDING_MODEL` / `EMBEDDING_DIM` — sentence-transformers (default `all-MiniLM-L6-v2`, 384-d)
- `OPENROUTER_API_KEY`, optional `OPENROUTER_MODEL` override
- `LLM_ROUTING_DEFAULT_PLUG`, `LLM_ROUTING_QUALITY_PLUG`, `LLM_ROUTING_FAST_PLUG` — auto-routing
- `LLM_ROUTING_STRONG_SIMILARITY_THRESHOLD` — minimum semantic similarity for strong/fast routing (default `0.35`)

## Migrations

```bash
make migrate-db
# or
docker compose exec fastapi_app alembic upgrade head
```

## Tests

```bash
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
pytest tests/unit -q
make test   # all tests when integration DB is available
```

## Evaluations

Requires indexed content and `OPENROUTER_API_KEY` for non-mock answers:

```bash
make run-evals
make save-baseline
```

## Architecture notes

- **Vectors** live in Postgres (`document_chunks.embedding`) with HNSW (cosine).
- **Full-text** uses a generated `tsvector` column + GIN index.
- **Retrieval** fuses semantic + keyword ranks with RRF.
- **Ingestion** runs in FastAPI `BackgroundTasks` (parse → chunk → batch embed → persist).

Refer to [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for the long-term phased roadmap.
