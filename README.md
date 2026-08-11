# Weather Tracking & Analysis Dashboard

[![Backend CI](https://github.com/pop134/sample_PM_v3/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/pop134/sample_PM_v3/actions/workflows/backend-ci.yml) [![Frontend CI](https://github.com/pop134/sample_PM_v3/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/pop134/sample_PM_v3/actions/workflows/frontend-ci.yml)

Web application that ingests weather data from external providers, stores and
analyses time-series history, and presents current conditions, trends and alerts
through an interactive dashboard.

## Repository layout
| Path         | Description                                             |
|--------------|---------------------------------------------------------|
| `backend/`   | FastAPI service: ingestion, API, analytics (Python)     |
| `frontend/`  | React + TypeScript + Vite dashboard SPA                 |
| `docs/`      | Architecture and roadmap notes                          |
| `.github/`   | CI workflows                                             |

## Quick start
```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp ../.env.example .env
uvicorn app.main:app --reload   # http://localhost:8000/docs

# Frontend (separate terminal)
cd frontend
npm install
npm run dev                     # http://localhost:5173
```
Or run both with Docker: `docker compose up --build`.

## Project management
Work is planned in `Weather_Dashboard_WBS.xlsx` and delivered through pull
requests, each scoped to a single WBS task (often split across several PRs).
See [docs/ROADMAP.md](docs/ROADMAP.md) for the WBS-to-code mapping.
