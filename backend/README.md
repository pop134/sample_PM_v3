# Backend — Weather Tracking & Analysis Dashboard

FastAPI service that ingests weather data, stores time-series history, and
exposes it through a documented REST API.

## Stack
- FastAPI + Uvicorn
- SQLAlchemy 2.x (SQLite for local dev / tests)
- Pydantic v2 + pydantic-settings
- httpx for provider calls
- pytest for tests

## Local development
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp ../.env.example .env
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

## Tests
```bash
pytest
```
