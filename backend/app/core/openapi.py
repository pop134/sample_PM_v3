"""OpenAPI metadata (WBS 1.2.4).

Central description, tag groups and contact/license used to document the API so
the frontend can integrate against a clear contract.
"""
from __future__ import annotations

API_DESCRIPTION = """
The **Weather Tracking & Analysis Dashboard** API exposes ingested weather
observations, location metadata, analytics and user authentication.

* **weather** — current conditions and historical time-series queries
* **locations** — tracked places
* **auth** — registration, login (JWT bearer) and the current user
* **system** — health and readiness

Authenticate by sending `Authorization: Bearer <token>` obtained from
`POST /api/auth/login`.
"""

TAGS_METADATA = [
    {"name": "weather", "description": "Current conditions & historical queries."},
    {"name": "locations", "description": "Tracked locations metadata."},
    {"name": "auth", "description": "Registration, login and current user."},
    {"name": "system", "description": "Health & readiness probes."},
]

CONTACT = {"name": "Weather Dashboard Team", "url": "https://example.com/weather"}
LICENSE = {"name": "MIT", "url": "https://opensource.org/licenses/MIT"}
