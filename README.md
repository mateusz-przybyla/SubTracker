# SubTracker

Flask REST API for managing subscriptions (Netflix, Spotify, etc.) with reminders for upcoming payments and monthly summary reports.  
Includes JWT authentication, MySQL, Redis, background jobs with RQ, scheduled tasks via RQ Scheduler, Mailgun integration, Docker setup and extensive test coverage.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
    - [Local setup](#local-setup)
    - [Docker setup](#docker-setup)
- [Database Schema](#database-schema)
- [Endpoints](#endpoints)
    - [Auth](#auth)
    - [User management](#user-management)
    - [Subscriptions](#subscriptions)
    - [Reminders](#reminders)
    - [Reminder logs](#reminder-logs)
    - [Stats](#stats)
- [Validation and Errors](#validation-and-errors)
- [Background Jobs and Emails](#background-jobs-and-emails)
- [Architecture Overview](#architecture-overview)
- [Testing](#testing)
- [Postman Collection](#postman-collection)

---

## Features

- JWT authentication (access + refresh tokens)
- Token revocation stored in **Redis**
- MySQL database with **SQLAlchemy** and **Flask-Migrate**
- Background job queue using **RQ** and **Redis**
- Scheduled jobs with **RQ Scheduler**:
    - Daily reminders for upcoming subscription payments
    - Monthly spending summary reports
- Email sending via **Mailgun API**
- API documentation with **Swagger UI** (via Flask-Smorest) available at [`/swagger-ui`](http://localhost:5000/swagger-ui)
- Database migrations with **Flask-Migrate / Alembic**
- Environment variable support via `.env` / `.flaskenv`
- Docker and docker-compose setup
- Unit, service, worker and integration tests with **pytest**
- Test coverage: **92%**
- Postman collection with all endpoints and variables

---

## Requirements

- Python 3.13
- Flask
- Flask-Smorest
- SQLAlchemy
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- Passlib
- python-dotenv
- Redis
- requests
- rq
- rq-scheduler
- pymysql
- cryptography
- Docker & Docker Compose

See [requirements.txt](requirements.txt) and [requirements-dev.txt](requirements-dev.txt).

---

## Installation

### Docker setup

- Clone repository

```bash
git clone https://github.com/mateusz-przybyla/SubTracker.git
cd Subtracker
```

- Copy environment variables file

```bash
copy .env.example .env (Windows Powershell)
# then edit .env and set your values, e.g.:

# --- Flask / JWT ---
JWT_SECRET_KEY=your_jwt_secret_key

# --- Database (MySQL) ---
DATABASE_URL=mysql+pymysql://user:password@db:3306/subtracker
DB_ROOT_PASSWORD=root
DB_DATABASE=subtracker
DB_USERNAME=user
DB_PASSWORD=password

# --- Redis ---
REDIS_URL=redis://redis:6379

# --- Mailgun ---
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=your-domain.mailgun.org
```

- Build image and start containers

```bash
docker compose up -d --build
```

- Run migrations inside container

```bash
docker compose exec web flask db upgrade
```

- Check logs

```bash
docker compose logs -f
```

- Stop and remove containers

```bash
docker compose down
```

---

## Database schema

![](/readme/database-schema.jpg)

---

## Endpoints

### Auth
- **POST** `/register` – register new user
- **POST** `/login` – login and get tokens
- **POST** `/refresh` – refresh access token
- **POST** `/logout` – revoke refresh token

### User management
- **GET** `/users/<id>` – fetch user by id
- **DELETE** `/users/<id>` – delete user
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

### Developer Endpoints (optional)
- **GET** `/guest` – open endpoint, no authentication required
- **GET** `/protected` – requires valid JWT token
- **GET** `/fresh-protected` – requires fresh JWT token
- **POST** `/reminders/send-test` – send a test reminder email (developer only)
- **POST** `/stats/send-test` – send a test stats summary email (developer only)

---

## Validation and Errors

- JWT errors → `401 Unauthorized`
- Validation errors → `422 Unprocessable Entity`
- Resource errors → `404 Not Found`, `409 Conflict`
- Database errors → `500 Internal Server Error`

---

## Background Jobs and Emails

- **Reminder worker** (`reminder_worker.py`)
Runs daily, checks upcoming subscription payments, sends reminder emails and logs results in `reminder_logs`.
- **Report worker** (`report_worker.py`)
Runs monthly, generates spending summaries for all users, sends summary emails and logs results via `app.logger`.
- **Mail worker** (`mail_worker.py`)
Handles queued email jobs (welcome emails, reminders, reports).

Jobs are scheduled via `scheduler.py` using **RQ Scheduler**.
Both reminder and report workers rely on the Flask **application context** (`app.app_context()`), ensuring they can access database models, configuration and services defined in the API layer.

---

## Architecture Overview

The API is designed with a clear separation of concerns between the web layer, background workers, queues and persistence.

## Components

- **Flask REST API**
    - Endpoints for authentication, user management, subscriptions, reminders, reminder logs and stats.
    - Uses **Flask-Smorest** for schema validation and auto-generated Swagger docs.
    - JWT authentication with Redis-backed token revocation.
- **Database (MySQL)**
    - Stores users, subscriptions and reminder logs.
    - Managed via **SQLAlchemy ORM** and **Alembic migrations**.
- **Redis**
    - Broker for background jobs.
    - Stores revoked JWT tokens.
- **RQ Queues & Workers**
    - `rq_worker_emails` → handles email sending jobs.
    - `rq_worker_reminders` → daily subscription payment reminders.
    - `rq_worker_reports` → monthly spending summary reports.
- **Scheduler**
    - `rq_scheduler` → runs RQ Scheduler process, responsible for recurring jobs.
    - `register_jobs` → one‑shot container that registers jobs (daily reminders, monthly reports) into the scheduler.
- **Docker & Compose**
    - Containers for API, MySQL, Redis, workers, scheduler and job registration.
    - Simplifies local development and deployment.

---

## Testing

Run all tests:

```bash
pytest -v
```

Run all tests with coverage:

```bash
pytest -v --cov=api tests/
```

Run all tests with coverage via Docker:

```bash
docker-compose exec web pytest -v --cov=api tests/
```

Test structure:
- `tests/unit/` → models, schemas, helpers
- `tests/service/` → service layer
- `tests/workers/` → background workers
- `tests/integration/` → auth/subs/stats/reminder flow

Coverage: **92%**

---

## Postman Collection

A Postman collection with all endpoints and environment variables is included in the repository `postman/`.
Import it into Postman to test authentication, subscriptions, reminders and reports easily.