# SubTracker

Flask REST API for managing subscriptions (Netflix, Spotify, etc.) with reminders for upcoming payments and monthly summary reports.

The system was designed with a strong focus on real-world backend challenges such as background processing, task scheduling, failure handling and scalable architecture.

---

## Table of Contents

- [Features](#features)
- [Real-world Problems Solved](#real-world-problems-solved)
- [Tech Stack](#tech-Stack)
- [Database Schema](#database-schema)
- [Architecture Overview](#architecture-overview)
    - [Core Components](#core-components)
    - [Queues & Workers](#queues--workers)
- [Endpoints](#endpoints)
    - [Auth](#auth)
    - [Subscriptions](#subscriptions)
    - [Reminders](#reminders)
    - [Reminder logs](#reminder-logs)
    - [Stats](#stats)
- [Quick Start (Docker)](#quick-start-docker)
- [Testing](#testing)
- [Postman Collection](#postman-collection)
- [Possible Improvements](#possible-improvements)
- [Status](#status)

---

## Features

- JWT authentication: access + refresh tokens
- Token revocation stored in Redis
- Subscription management (CRUD)
- Asynchronous background jobs (REDIS + RQ)
- Scheduled tasks (reminders and monthly reports)
- Email notifications via Mailgun
- Reminder logs with success/failure tracking
- REST API documentation (Swagger UI)
- Dockerized environment (API, DB, Redis, workers, scheduler)
- 90% test coverage (unit, service, integration)

---

## Real-world Problems Solved

- Background processing\
Each reminder and report is processed as an isolated job with retry capability.
- Task separation & scalability\
Independent queues and workers for emails, reminders and reports allow horizontal scaling.
- Failure handling & observability\
Every reminder attempt is logged (success/failure).
- Recurring job scheduling\
Daily and monthly processes handled via cron-like scheduler.
- Secure authentication lifecycle\
JWT with refresh tokens and Redis-based revocation.

---

## Tech Stack

- Python 3.13
- Flask + Flask-Smorest
- SQLAlchemy + Alembic
- MySQL
- Redis + RQ + RQ Scheduler
- JWT (flask-jwt-extended)
- Mailgun API
- Docker & Docker Compose
- Pytest

See [requirements.txt](requirements.txt) and [requirements-dev.txt](requirements-dev.txt).

---

## Database schema

![](/readme/database_schema.png)

---

## Architecture Overview

- API Layer (controllers)
    - Flask routes (endpoints)
    - Request validation (schemas)
    - Authentication (JWT)
- Business Logic (services)
    - Services handling application logic and database interactions
- Data Layer (models)
    - SQLAlchemy models representing database structure
- Background Processing (tasks)
    - Asynchronous tasks executed by workers (Redis + RQ)
    - Separate queues for emails, reminders and reports
    - Scheduled jobs for recurring tasks (daily reminders, monthly reports)

## Endpoints

### Auth
- **POST** `/register` – register new user
- **POST** `/login` – login and get tokens
- **POST** `/refresh` – refresh access token
- **POST** `/logout` – revoke refresh token
- **GET** `/users/me` – fetch current user profile

### Subscriptions
- **GET** `/subscriptions` – list subscriptions
- **POST** `/subscriptions` – create subscription
- **GET** `/subscriptions/<sub_id>` – get subscription details
- **PUT** `/subscriptions/<sub_id>` – update subscription
- **DELETE** `/subscriptions/<sub_id>` – delete subscription

### Reminder logs
- **GET** `/subscriptions/<sub_id>/reminder_logs` – list reminder logs for subscription
- **GET** `/reminder_logs/<log_id>` – fetch single reminder log
- **DELETE** `/reminder_logs/<log_id>` – delete reminder log

### Reminders
- **GET** `/reminders/upcoming?days=<int>` - list upcoming subscription payments for the authenticated user within the specified number of days.  

### Reports
- **GET** `/stats/summary?month=<YYYY-MM>` - retrieve a monthly spending summary for the authenticated user.

---

## Quick Start (Docker)

```bash
git clone https://github.com/mateusz-przybyla/SubTracker.git
cd Subtracker
```

- Copy environment variables file

```bash
copy .env.example .env (Windows Powershell)
# configure environment variables
```

```bash
docker compose up -d --build
```

```bash
docker compose exec web flask db upgrade
```

---

## Testing

```bash
pytest -v
```

```bash
pytest -v --cov=api tests/
```

```bash
docker-compose exec web pytest -v --cov=api tests/
```

Test structure:
- `tests/unit/`
- `tests/service/`
- `tests/integration/`

Coverage: **90%**

---

## Postman Collection

A Postman collection with all endpoints and environment variables is included in the repository `/postman`.
Import it into Postman to test authentication, subscriptions, reminders and reports easily.

---

## Possible Improvements

- Idempotency (duplicate job protection)
- Monitoring (e.g. Prometheus / Grafana)

## Status

Project actively developed as a portfolio backend system.