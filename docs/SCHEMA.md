# Database Schema (WBS 1.2.1)

SQLite for local dev/tests; the models are portable to PostgreSQL/TimescaleDB in
production. Migrations are introduced under WBS 1.7 (`init_db()` is used for
dev/test convenience today).

## Metadata tables
### `users`
Auth + preferences owner. `id`, `email` (unique), `hashed_password`,
`is_active`, `is_admin`, `created_at`.

### `locations`
Tracked places driving ingestion. `id`, `name` (indexed), `latitude`,
`longitude`, `created_at`. Managed via `LocationRepository`.

## Time-series tables
### `observations`
Normalised readings. Columns: coordinates, `observed_at`, weather metrics,
`provider`, `created_at`.
- **Unique**: `(latitude, longitude, observed_at, provider)` — dedup.
- **Composite index** `ix_observation_point_time (latitude, longitude, observed_at)`
  — the dominant "a location's readings over a range" query.

### `forecasts`
Predicted points for later accuracy analysis. Coordinates, `target_time`,
`generated_at`, metrics, `provider`.
- **Unique**: `(latitude, longitude, target_time, provider)` — newest generation
  upserts.

## Access patterns
| Query | Index used |
|-------|------------|
| Latest reading for a location | `ix_observation_point_time` (desc scan) |
| Range of readings for a location | `ix_observation_point_time` |
| Forecast for a target time | `ix_forecasts_target_time` + point indexes |
| User lookup by email (login) | unique `users.email` |

## Partitioning note
In production, `observations` is a natural candidate for time-based partitioning
(e.g. monthly) or a TimescaleDB hypertable on `observed_at`.
