# Roadmap — WBS to Code

The build follows the Work Breakdown Structure in `Weather_Dashboard_WBS.xlsx`.
Each pull request maps to **at most one WBS task**; larger tasks are split
across multiple PRs.

## 1.1 Weather Data Ingestion & Integration
- **1.1.1 [BE] Integrate external weather data providers**
  - Part 1 — provider abstraction, canonical DTOs, config & registry (`app/providers/`)
  - Part 2 — OpenWeatherMap client + response parsing
- 1.1.2 [BE] Scheduled ingestion & polling jobs
- 1.1.3 [BE] Normalise & store time-series weather data
- 1.1.4 [BE] Rate limiting, retries & response caching

## 1.2 Backend Core API & Data Services
- 1.2.1 Schema · 1.2.2 REST API · 1.2.3 Auth · 1.2.4 OpenAPI docs

## 1.3 Weather Analytics Engine
- 1.3.1 Trends/aggregation · 1.3.2 Anomaly & alerts · 1.3.3 Forecast vs. actual

## 1.4 Dashboard UI & Visualization
- 1.4.1 Project & design system · 1.4.2 Layout/nav/theming · 1.4.3 Current widgets
- 1.4.4 Charts · 1.4.5 Location search · 1.4.6 Responsive

## 1.5 Frontend Data & State Integration
- 1.5.1 API client · 1.5.2 State/caching · 1.5.3 Loading/error states · 1.5.4 Real-time

## 1.6 Alerts & User Preferences
- 1.6.1 [BE] Preferences API · 1.6.2 [FE] Settings UI

## 1.7 QA, Testing & Deployment
- 1.7.1 Backend tests · 1.7.2 Frontend tests · 1.7.3 CI/CD · 1.7.4 Monitoring

## Status
- [x] Project foundation & scaffolding
- [x] 1.1.1 [BE] Integrate external weather data providers (parts 1 & 2)
- [ ] 1.1.2 (next)
