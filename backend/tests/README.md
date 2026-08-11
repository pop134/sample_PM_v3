# Backend tests (WBS 1.7)

```bash
cd backend
pip install -r requirements-dev.txt
pytest                     # run everything
pytest --cov=app           # with coverage (pytest-cov)
```

## Layout
- **Unit** — pure logic per feature: `test_normalization`, `test_analytics`,
  `test_anomaly`, `test_forecast_accuracy`, `test_retry`, `test_resilience`,
  `test_scheduler`, `test_security`, …
- **Repository/DB** — in-memory SQLite: `test_observation_store`,
  `test_location_store`, `test_preferences_store`, …
- **API integration** — `TestClient` + `get_db` override on a `StaticPool`
  in-memory DB: `test_weather_api`, `test_auth_api`, `test_analytics_api`,
  `test_alerts_api`, `test_accuracy_api`, `test_preferences_api`.
- **End-to-end** — ingest → store → API: `test_end_to_end`.
- **Contract** — provider HTTP via `respx` (`test_provider_contract`) and the
  published OpenAPI shape (`test_api_contract`).

No test makes a real network call or needs a running server.
