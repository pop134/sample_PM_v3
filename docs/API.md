# API Guide (WBS 1.2.4)

Base URL: `/api`. Interactive docs at `/docs` (Swagger UI) and `/redoc`.
The machine-readable contract is `/openapi.json`, or export it offline:

```bash
cd backend
python -m scripts.export_openapi openapi.json
```

## Authentication
Obtain a token, then send `Authorization: Bearer <token>`.

```bash
# Register
curl -X POST /api/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"me@example.com","password":"pw123456"}'

# Login -> { "access_token": "...", "token_type": "bearer" }
curl -X POST /api/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"me@example.com","password":"pw123456"}'

# Current user
curl /api/auth/me -H 'Authorization: Bearer <token>'
```

## Weather
```bash
# Current conditions (404 if no data for the location)
curl '/api/weather/current?lat=51.5074&lon=-0.1278'

# History (paginated; limit<=500)
curl '/api/weather/history?lat=51.5074&lon=-0.1278&limit=50&offset=0'
```
Example current response:
```json
{
  "id": 1, "location_name": "London",
  "latitude": 51.5074, "longitude": -0.1278,
  "observed_at": "2026-08-01T18:00:00Z",
  "temperature_c": 18.0, "humidity_pct": 72.0,
  "wind_speed_ms": 4.1, "condition": "light rain",
  "provider": "openweather"
}
```

## Locations
```bash
curl /api/locations           # list
curl /api/locations/1         # by id (404 if unknown)
```

## Error model
Errors use the standard FastAPI shape: `{ "detail": "<message>" }` with an
appropriate status code (400 bad range, 401 unauthenticated, 403 forbidden,
404 not found, 409 conflict, 422 validation).
