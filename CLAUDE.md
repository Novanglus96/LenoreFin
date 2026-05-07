# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LenoreFin is a self-hosted personal finance tracking application. The stack is:
- **Backend**: Django 4.2.3 + Django Ninja (REST API) + PostgreSQL + Redis (via django-q2)
- **Frontend**: Vue 3 + Vite + Vuetify 3 + Pinia + TanStack Query
- **Task Queue**: django-q2 (`qcluster` worker)
- **Deployment**: Docker Compose + Gunicorn + Nginx

## Development Commands

### Full Stack (Docker — recommended)

```bash
docker compose up -d          # Start all services (frontend, backend, worker, db, redis)
docker compose logs -f backend
docker compose down
```

Services: frontend at `:8081`, backend API at `:8001`, MkDocs at `:8002`

### Backend (manual)

```bash
cd backend
python manage.py runserver 0.0.0.0:8001
python manage.py qcluster          # Task queue worker (separate terminal)
mkdocs serve --dev-addr=0.0.0.0:8002
```

### Frontend (manual)

```bash
cd frontend
npm install
npm run serve     # Vite dev server at :5173
npm run build
npm run lint      # ESLint with auto-fix
npm run format    # Prettier
```

### Backend Tests

```bash
cd backend
pytest                              # All tests
pytest -m unit                      # By marker: unit, service, api
pytest accounts/tests/              # Specific app
pytest accounts/tests/api/test_forecast_api.py  # Specific file
pytest -v                           # Verbose
```

Test markers: `@pytest.mark.unit`, `@pytest.mark.service`, `@pytest.mark.api`

Test fixtures are in `conftest.py` at the repo root. `api_client` is the Django Ninja `TestClient`.

### Linting

Ruff is the linter (not flake8 — use the full path per global CLAUDE.md rules). Also:

```bash
cd frontend
npm run lint
```

## Architecture

### Backend Django Apps

The API is built with **Django Ninja** and registered centrally in `backend/backend/api.py`. All routes are under `/api/v1/` with global `GlobalAuth` authentication.

| App | Responsibility | Key Routes |
|-----|---------------|------------|
| `accounts` | Bank accounts, account types, forecasting | `/accounts`, `/accounts/forecast` |
| `transactions` | Transactions, paychecks, statuses | `/transactions`, `/transactions/paychecks` |
| `tags` | Tag hierarchy (MainTag → SubTag → Tag), analytics | `/tags`, `/tags/graph-by-tags` |
| `planning` | Budget, contributions, retirement, calculator | `/planning/budget`, `/planning/contributions` |
| `reminders` | Bill reminders, recurring events | `/reminders` |
| `imports` | CSV/file import pipeline | `/file-imports` |
| `administration` | Payees, options, system messages, versioning | `/administration/options`, `/administration/version` |
| `core` | Shared DTOs, cache utilities | (no routes) |

Each app follows the pattern: `models.py` → `services/` → `api/` (Django Ninja routers) with `dto/` and `mappers/` for data transformation.

### Frontend Structure

- **Router**: `src/router/` — all page routes
- **Stores** (Pinia): `main`, `planning`, `transactions`, `themeStore`
- **Data fetching**: TanStack Vue Query (`@tanstack/vue-query`) for server state
- **UI**: Vuetify 3 components throughout; Chart.js for graphs
- Vite dev proxy points to the backend API configured in `frontend/vite.config.js`

### Data Flow

```
Vue 3 frontend (Vuetify + Pinia + TanStack Query)
  ↕ Nginx reverse proxy
  ↕ Django Ninja REST API (/api/v1/)
  ↕ PostgreSQL
     + Redis → django-q2 worker (scheduled/async tasks)
```

### Startup & Fixtures

On dev startup (`backend/start.dev.sh`), the backend automatically runs migrations and loads seed fixtures:
- Account types, banks, transaction types/statuses, tag types/maintags/subtags/tags, repeat types, graph types
- Management commands: `scheduletasks`, `load_version_fixture`, `load_options`, `load_caches`

When adding new required reference data, add a fixture and load it in `start.dev.sh`.

### Settings

The main Django settings file is `backend/backend/settings.py`. Test overrides are in `backend/backend/settings_test.py`. Key env vars are defined in `.env.dev` (see `example.env` for the full list).
