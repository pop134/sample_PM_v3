# Frontend — Weather Tracking & Analysis Dashboard

React 18 + TypeScript + Vite single-page app for the weather dashboard.

## Local development
```bash
cd frontend
npm install
npm run dev
```
The dev server proxies `/api` to the backend at `http://localhost:8000`.

## Scripts
- `npm run dev` — start the dev server
- `npm run build` — type-check and production build
- `npm run lint` — type-check only
- `npm run test` — run unit tests (Vitest)

## End-to-end tests (WBS 1.7.2)
Playwright specs live in `e2e/`.
```bash
npm install
npx playwright install    # one-time: download browsers
npm run test:e2e          # starts the dev server and runs the flows
```
E2E is intentionally separate from `npm test` (Vitest unit/component tests) so
the default CI job stays fast; wire it into a dedicated CI job when a browser
runner is available.
