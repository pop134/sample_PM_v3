# Deployment (WBS 1.7.3)

## Pipelines
- **Backend CI** / **Frontend CI** (`.github/workflows/*-ci.yml`) — run on every
  push/PR: backend pytest, frontend `tsc` build + Vitest.
- **Release** (`.github/workflows/release.yml`) — on a `v*` tag (or manual
  dispatch): builds the backend and frontend images and pushes them to the
  GitHub Container Registry (`ghcr.io/<owner>/<repo>/{backend,frontend}`), with
  layer caching.

Cut a release:
```bash
git tag v0.1.0 && git push origin v0.1.0
```

## Run the stack
Local (hot-reload):
```bash
docker compose up --build
```
Production-style (nginx-served frontend on :80):
```bash
SECRET_KEY=$(openssl rand -hex 32) \
OPENWEATHER_API_KEY=... \
docker compose -f docker-compose.prod.yml up --build -d
```

## Configuration
See `.env.example`. Required in production: `SECRET_KEY`. Optional:
`OPENWEATHER_API_KEY`, `DATABASE_URL` (default SQLite; point at Postgres for a
real deployment), `POLL_INTERVAL_SECONDS`.

## Health
Both services expose Docker healthchecks; the backend's is `GET /api/health`.
