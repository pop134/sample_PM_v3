# Monitoring, Logging & Alerting (WBS 1.7.4)

## Logging
Structured, greppable stream logs via `configure_logging()`:
```
2026-08-11 10:00:00 level=INFO logger=request msg=request id=ab12cd34ef56 method=GET path=/api/health status=200 duration_ms=1.4
```
Every request is logged (method, path, status, duration) with a correlation
`X-Request-ID` also returned on the response, ready to ship to a central
aggregator (e.g. Loki/ELK).

## Metrics
- **`GET /api/metrics`** — in-process counters: `http_requests_total`,
  `http_responses_{2,4,5}xx_total`, `http_errors_total`. Swap the registry for a
  Prometheus client in production and scrape it.

## Health & readiness
- **`GET /api/health`** — liveness (process up).
- **`GET /api/health/ready`** — readiness; runs `SELECT 1` and returns **503**
  if the database is unreachable. Use these as container/orchestrator probes.

## Alerting
`app/core/alerting.py` provides pure predicates over the metrics snapshot:
- `error_rate(snapshot)` and `should_page(snapshot, threshold, min_requests)`.
- `check_and_log(snapshot)` emits an `ERROR` log line (`ALERT api_error_rate …`)
  when the sustained 5xx rate crosses the threshold.

Wire `check_and_log` to a scheduled poll (the `PeriodicScheduler` from 1.1.2) and
route the ERROR logs / a webhook to your pager. Ingestion failures are already
logged with counts by the ingestion job (1.1.2).
