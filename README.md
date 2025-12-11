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
    - [User management](#user-management)
    - [Subscriptions](#subscriptions)
    - [Reminders](#reminders)
    - [Reminder logs](#reminder-logs)
    - [Stats](#stats)
- [Validation and Errors](#validation-and-errors)
- [Testing](#testing)
- [Postman Collection](#postman-collection)

---

## Features

- JWT authentication: access + refresh tokens
- Token revocation stored in **Redis**
- **MySQL** + SQLAlchemy ORM + Alembic migrations
- **Redis** + **RQ** for async background tasks
- **RQ Scheduler** for recurring jobs:
    - Daily: `check_upcoming_payments`
    - Monthly: `send_monthly_user_reports`
- Email delivery via **Mailgun API**
- API documentation via **Flask-Smorest / Swagger UI** at `/swagger-ui`
- Environment configuration via `.env` and `.flaskenv`
- Docker Compose including API, DB, Redis, workers & scheduler
- Unit, service and integration tests with **pytest**
- Test coverage: **92%**
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

![](/readme/database-schema.jpg)

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

- **Email Worker** (`rq_worker_emails`)
Sends transactional emails (welcome, reminders, monthly summaries).

- **Reminder Worker** (`rq_worker_reminders`)
Runs `check_upcoming_payments`, sends upcoming payment emails and creates reminder logs.

- **Report Worker** (`rq_worker_reports`)
Generates and emails monthly summaries for all users.

### Scheduler (Recurring Jobs)

Recurring tasks are managed using **RQ Scheduler**, running in its own container:

- `rq_scheduler` – scheduler process
- `register_jobs` – one-shot container that registers recurring jobs on startup

Registered jobs:

- `check_upcoming_payments`
    - Runs: **every 24 hours**
    - Processed by: **Reminder Worker**
    - Purpose: Sends upcoming payment reminders and creates reminder logs.
- `send_monthly_user_reports`
    - Runs: **every 30 days**
    - Processed by: **Report Worker**
    - Purpose: Generates and sends monthly spending summaries to all users.

### Task Layer

Tasks encapsulate business logic used by workers:

- **Email Task** (`send_user_registration_email` / `send_email_reminder` / `send_monthly_report_email`)
Sends emails via the Mailgun API.

- **Reminder Task** (`check_upcoming_payments`)
Finds subscriptions due soon (1 or 7 days), queues appropriate emails, writes reminder logs.

- **Report Task** (`send_monthly_user_reports`)
Aggregates user spending per month and sends summary emails.\

Reminder and Report Tasks executed by workers run inside the Flask application context (`with app.app_context()`), allowing them to access the database, models, configuration and service layer.

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
- `tests/unit/` → models, schemas, blocklist, helpers
- `tests/service/` → service layer
- `tests/integration/` → tasks, resources

Coverage: **92%**

---

## Postman Collection

A Postman collection with all endpoints and environment variables is included in the repository `postman/`.
Import it into Postman to test authentication, subscriptions, reminders and reports easily.