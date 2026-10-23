# Smart Electricity Billing & Management System

A Django REST backend and Next.js frontend for electricity billing and operational workflows. The project separates consumer, meter-reading, office-staff, billing, payment, and user-management responsibilities into application modules.

## Features

- JWT login, token refresh, logout, and current-user APIs
- Role-specific workflows for consumers, meter readers, office staff, and SDO users
- Slab-based electricity bill calculations using decimal arithmetic
- Celery tasks for monthly bill generation
- Billing and payment APIs
- Next.js frontend built with React and TypeScript
- Automated tests for authentication, billing, consumers, meter readings, payments, tariffs, and access control

## Technology stack

| Layer | Technologies |
| --- | --- |
| API | Python, Django, Django REST Framework |
| Authentication | Simple JWT |
| Background processing | Celery, Redis |
| Database support | PostgreSQL |
| Frontend | Next.js, React, TypeScript |
| Tests | pytest; development dependencies in requirements-dev.txt |

## Architecture

The frontend calls the Django REST API. Django application modules handle validation, permissions, and persistence. Billing calculation logic is separated into `core/services/billing.py`, while monthly generation runs through Celery in `bill/tasks.py`. Redis supports the background-task configuration.

| Path | Responsibility |
| --- | --- |
| `SEBMS/` | Django project configuration and root URLs |
| `users/` | Authentication and user management |
| `consumer/` | Consumer workflows |
| `meterreader/` | Meter-reading workflows |
| `officestaff/` and `SDO/` | Staff workflows |
| `bill/` | Billing APIs and generation tasks |
| `core/` | Shared backend logic, including billing calculations |
| `payment/` | Payment workflows |
| `frontend/` | Next.js application |
| `tests/` | Automated backend tests |

## Billing design

- Slab calculations use `Decimal` arithmetic rather than binary floating-point money calculations.
- The billing service defines four usage bands: the first 100 units, the next 100, the next 100, and remaining units.
- The calculation includes a 15-day due period and a 10% late fee.
- Monthly generation uses background tasks with retry and execution-time limits.
- Transactional bulk creation and meter/month uniqueness support consistent bill generation.

These describe implementation rules, not measured production performance.

## API overview

The API is mounted under `/api/v1/`.

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/auth/login/` | Obtain authentication tokens |
| POST | `/api/v1/auth/refresh/` | Refresh an access token |
| POST | `/api/v1/auth/logout/` | Logout/token handling |
| GET | `/api/v1/auth/me/` | Read the authenticated user |
| POST | `/api/v1/bills/generate/` | Request bill generation; office-staff permission required |

Additional route groups cover users, consumers, meter readers, bills, payments, office staff, and SDO operations. Refer to `SEBMS/urls.py` and the application URL files for the complete route inventory and exact request contracts.

## Local development

### Prerequisites

- Python compatible with `requirements.txt`
- Node.js/npm compatible with `frontend/package.json`
- PostgreSQL and Redis configured for your local environment

### Backend

```bash
git clone https://github.com/zanamarmani/SEBMS-Final.git
cd SEBMS-Final
python -m venv .venv
```

Activate the environment using the command for your shell:

```bash
# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and configure the database, Redis, email, authentication, and frontend-origin settings required for your environment. Use the variable names in the supplied example and the Django settings as the source of truth.

With the required services running:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Monthly background processing also requires a Celery worker configured for this Django project. Check the Celery configuration under `SEBMS/` before choosing worker and scheduling commands.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Configure the frontend API URL to match the backend. Consult `frontend/package.json` for the available build and startup scripts.

## Tests

From the repository root, with the backend environment active:

```bash
pip install -r requirements-dev.txt
pytest
```

See `pytest.ini` and `tests/` for test configuration and coverage areas. Test results depend on the current revision and local service configuration; no passing-test count or coverage percentage is asserted here.

## Project scope

This repository demonstrates electricity-billing application design, role-specific APIs, background processing, and frontend integration. A tracked SQLite database is not required as a substitute for configuring a clean local database. Use synthetic development data and environment-specific configuration.
