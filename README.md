# SubTracker

Flask REST API for managing subscriptions (Netflix, Spotify, etc.) with reminders for upcoming payments and monthly summary reports.  
Includes JWT authentication, MySQL, Redis, background jobs with RQ, scheduled tasks via RQ Scheduler, Mailgun integration, Docker setup and extensive test coverage.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
    - [Docker setup](#docker-setup)
- [Database Schema](#database-schema)
- [Architecture Overview](#architecture-overview)
- [Endpoints](#endpoints)
    - [Auth](#auth)
    - [Subscriptions](#subscriptions)
    - [Reminders](#reminders)
    - [Reminder logs](#reminder-logs)
    - [Stats](#stats)
    - [Developer endpoints](#developer-endpoints-optional)
- [Validation and Errors](#validation-and-errors)
- [Testing](#testing)
- [Postman Collection](#postman-collection)
- [Possible Production Improvements](#possible-production-improvements)
    - [Batch processing](#batch-processing)
    - [Idempotency and duplicate protection](#idempotency--duplicate-protection)

---

## Features

- JWT authentication: access + refresh tokens
- Token revocation stored in **Redis**
- **MySQL** + SQLAlchemy ORM + Alembic migrations
- **Redis** + **RQ** for async background tasks
- **RQ Scheduler** for recurring jobs:
    - Daily: `check_upcoming_payments`
    - Monthly: `generate_monthly_report`
- Email delivery via **Mailgun API**
- API documentation via **Flask-Smorest / Swagger UI** at `/swagger-ui`
- Environment configuration via `.env` and `.flaskenv`
- Docker Compose including API, DB, Redis, workers & scheduler
- Unit, service and integration tests with **pytest**
- Test coverage: **90%**
- Postman collection with all endpoints and variables

---

## Requirements

- Python 3.13
- Flask
- MySQL + SQLAlchemy
- Redis + RQ
- Mailgun
- Docker

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

![](/readme/database_schema.png)

---

## Architecture Overview

SubTracker is built with a clear separation of concerns between the web API, database layer, background workers, queues and scheduler. The system follows a modular, event-driven approach using Redis + RQ for async tasks and recurring jobs.

### Flask REST API Layer

- Endpoints for authentication, subscriptions, reminder logs and monthly statistics.
- Marshmallow schemas (Flask-Smorest) for validated request/response payloads.
- JWT authentication with access + refresh tokens.
- Redis-backed token revocation.
- Consumes service layer functions (subscription service, reminder service).

### Database Layer (MySQL + SQLAlchemy)

Stores:
- Users
- Subscriptions
- Reminder logs

Managed via SQLAlchemy ORM and Alembic migrations.\
The reminder system records every reminder attempt in `ReminderLogModel` together with success/failure state, error message and timestamp.

### Redis Layer

Redis serves two independent roles:

- Backend for RQ queues.
- Storage for the JWT blocklist (revoked tokens).

### Asynchronous Processing (RQ Queues + Workers)

The system uses three isolated queues, each processed by a dedicated worker container:

#### Queues

- `email_queue` → outgoing email jobs
- `reminder_queue` → daily reminders
- `report_queue` → monthly reports

#### Workers

- **Email Worker** (`rq_worker_emails`)\
Sends transactional emails (welcome, reminders, monthly summaries).

- **Reminder Worker** (`rq_worker_reminders`)\
Executes reminder-related tasks and processes one reminder job per subscription,
sending emails and creating reminder logs.

- **Report Worker** (`rq_worker_reports`)\
Processes monthly report jobs, generating and emailing summaries per user.

Reminder and Report workers bootstrap the Flask application and execute jobs inside the Flask application context.
Email worker does not require application context as it does not access the database or Flask services.

### Scheduler (Recurring Jobs)

Recurring tasks are managed using **RQ Scheduler**, running in its own container:

- `rq_scheduler` – scheduler process
- `register_jobs` – one-shot container that registers recurring jobs on startup

Registered jobs:

- `check_upcoming_payments`
    - Runs: **once per day at a fixed time (cron)**
    - Processed by: **Reminder Worker**
    - Purpose: Enqueues reminder jobs (one per subscription) for upcoming payments due in 1 or 7 days.
- `generate_monthly_report`
    - Runs: **on the 1st day of each month at 00:00 (cron)**
    - Processed by: **Report Worker**
    - Purpose: Enqueues monthly report jobs (one per user) for the previous month..

### Task Layer

Tasks encapsulate asynchronous business logic executed by RQ workers:

- **Email Task** (`send_user_registration_email`, `send_email_reminder`, `send_monthly_summary_email`)\
Responsible only for sending emails via Mailgun.

- **Reminder Task** (`check_upcoming_payments`, `send_single_subscription_reminder`)\
Identify subscriptions with upcoming payments and enqueue **one reminder job per subscription**.
Each job sends a reminder email and persists reminder logs.

- **Report Task** (`send_monthly_user_reports`, `send_single_user_monthly_report`)\
Generate monthly spending summaries and enqueue **one report job per user**, ensuring isolated
processing and retryability.

---

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

### Developer Endpoints (optional)
- **GET** `/guest` – open endpoint, no authentication required
- **GET** `/protected` – requires valid JWT token
- **GET** `/fresh-protected` – requires fresh JWT token

- **GET** `/users/<id>` – fetch user by id
- **DELETE** `/users/<id>` – delete user by id

- **POST** `/reminders/send-test` – send a test reminder email
- **POST** `/stats/send-test` – send a test stats summary email

---

## Validation and Errors

- JWT errors → `401 Unauthorized`
- Validation errors → `422 Unprocessable Entity`
- Resource errors → `404 Not Found`, `409 Conflict`
- Database errors → `500 Internal Server Error`

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
- `tests/unit/`
- `tests/service/`
- `tests/integration/`

Coverage: **90%**

---

## Postman Collection

A Postman collection with all endpoints and environment variables is included in the repository `postman/`.
Import it into Postman to test authentication, subscriptions, reminders and reports easily.

---

## Possible Production Improvements

### Batch processing

Currently, orchestration tasks load all users or subscriptions into memory at once.
In a production system, this should be replaced with batch iteration, e.g.:

- iterating users in chunks (e.g. 1000 at a time) for report jobs
- iterating subscriptions in chunks for reminder jobs

This prevents excessive memory usage and allows better control over job enqueueing rate.

### Idempotency and duplicate protection

Currently, jobs assume "at most once" execution semantics.
In production, additional safeguards should be added, e.g.:

- Redis-based distributed locks per (user, month) or (subscription, date)
- Database-level uniqueness constraints for logs

This prevents duplicate emails in case of retries, crashes or scheduler misfires.