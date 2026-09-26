# KnovaultAI — AI Powered Knowledge Assistant

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

- `DATABASE_URL` — Postgres (default matches `docker-compose.yml`; use Supabase URI when deployed)
- `LOCAL_STORAGE_DIR` — uploaded file blobs when `STORAGE_BACKEND=local` (Docker volume `document_storage`)
- `STORAGE_BACKEND` — `local` (default) or `supabase` for Supabase Storage
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_STORAGE_BUCKET` — required when using Supabase Storage (server-only; never expose in the frontend)
- `EMBEDDING_MODEL` / `EMBEDDING_DIM` — sentence-transformers (default `all-MiniLM-L6-v2`, 384-d)
- `OPENROUTER_API_KEY`, optional `OPENROUTER_MODEL` override
- `LLM_ROUTING_DEFAULT_PLUG`, `LLM_ROUTING_QUALITY_PLUG`, `LLM_ROUTING_FAST_PLUG` — auto-routing
- `LLM_ROUTING_STRONG_SIMILARITY_THRESHOLD` — minimum semantic similarity for strong/fast routing (default `0.35`)

## Supabase (deploy / demo)

Hybrid setup: **Docker Compose** keeps local Postgres + `STORAGE_BACKEND=local`. For a hosted demo, point the API at Supabase:

1. Create a [Supabase](https://supabase.com) project.
2. **Database → Extensions** → enable **`vector`**.
3. **Storage** → create a **private** bucket (default name `documents`, or set `SUPABASE_STORAGE_BUCKET`).
4. **Project Settings → Database** → copy the **direct** connection URI (port 5432) into `DATABASE_URL` with `?sslmode=require`.
5. **Project Settings → API** → copy **Project URL** and **service role** key into `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` (API server only).
6. Set `STORAGE_BACKEND=supabase` and run migrations once: `alembic upgrade head`.

Uploaded files are stored under object keys `{kb_id}/{uuid}/{filename}` in the bucket; chunk embeddings remain in Postgres.

## Try demo (hosted portfolio)

Visitors use **Try demo** on the login page (passwordless JWT for a shared user). Upload and ingest are blocked for demo sessions (`can_upload: false` in JWT). You curate content by signing in with the **demo username and password** (same Supabase `DATABASE_URL` and storage from your machine).

**Hosted API `.env`:** `DEMO_LOGIN_ENABLED=true`, `DEMO_USERNAME=demo`, `ALLOW_PUBLIC_REGISTRATION=false`.

**Frontend build env:** `VITE_DEMO_LOGIN_ENABLED=true`, `VITE_ALLOW_REGISTRATION=false`.

**Once per environment:**

```bash
alembic upgrade head
DEMO_PASSWORD='your-strong-secret' python scripts/seed_demo_user.py
```

Then locally: log in as `demo` with that password, create knowledge bases, and upload documents—they appear for Try demo users.

## Render (API) checklist

**502 / “unable to handle this request”** means Render’s proxy cannot reach your app process.

1. **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (not `127.0.0.1`, not a fixed port).
2. **Health check path:** `/v1/health` (liveness only; DB is `/v1/ready`).
3. **Env values:** no surrounding `"` quotes in the Render dashboard (especially `DATABASE_URL`).
4. **`OTEL_EXPORTER_OTLP_ENDPOINT`:** leave unset or empty on Render.
5. **`SECRET_KEY`:** random string (e.g. `openssl rand -hex 32`); do not reuse the Supabase service role key.
6. **RAM:** PyTorch + embeddings often need **Starter** (512MB free tier may OOM or never become ready). See [render.yaml](render.yaml).
7. **Logs:** Render → Logs → look for `Out of memory`, `Killed`, or Python tracebacks on boot.

After deploy: `curl -s https://YOUR-SERVICE.onrender.com/v1/health`

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
