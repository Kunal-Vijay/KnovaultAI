# AI Knowledge Assistant — Frontend

React 19 + Vite + TypeScript + Tailwind CSS + shadcn-style UI.

## Development

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

- App: http://localhost:5173
- API requests use `/api` and are proxied to the backend (`VITE_API_PROXY_TARGET`, default `http://localhost:8000`).

With Docker Compose:

```bash
docker compose up frontend
```

The `frontend` service sets `VITE_API_PROXY_TARGET=http://fastapi_app:8000`. On start it runs `npm install` so the `frontend_node_modules` volume stays in sync with `package.json`.

If dependencies still look stale, reset the volume: `docker compose down` then `docker volume rm ai-knowledge-base_frontend_node_modules` (name may vary; check `docker volume ls`).

## Production static build

```bash
npm run build
npm run preview
```

Docker (nginx + API proxy):

```bash
docker compose --profile prod up frontend_prod
```

UI on http://localhost:8080

## Scripts

- `npm run dev` — Vite dev server
- `npm run build` — typecheck + production bundle
- `npm run test` — Vitest unit tests
- `npm run lint` — oxlint
