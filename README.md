# Service Scheduling API

Full stack application for service-based businesses — salons, clinics, studios — built with **React + Vite** and **FastAPI**.

---

## About

A complete scheduling platform where business owners manage their professionals, services, and appointments; clients book online without creating an account; and the system handles confirmations, reminders, and post-appointment reviews automatically.

---

## Tech Stack

### Frontend
- React + Vite
- FullCalendar (interactive weekly/monthly/daily view)
- Axios, React Router, React Toastify, React Icons, React Select
- Custom CSS with dark theme

### Backend
- FastAPI + SQLAlchemy + Alembic
- PostgreSQL (production) / SQLite (development/testing)
- Pydantic v2 — request/response validation
- JWT authentication (access + refresh tokens)
- Passlib — password hashing
- SlowAPI — rate limiting on public endpoints
- WeasyPrint — PDF report generation
- APScheduler (in-process threading) — automated reminders
- pytest — test suite

---

## Features

### Authentication
- Register and login with JWT (access + refresh tokens)
- Protected routes on both frontend and backend
- Forgot password → reset link sent by email (expires in 1 hour)
- Role-based access control: **owner** (full access) and **professional** (own agenda only)

### Client Management
- Create, edit, delete clients
- CPF validation (digit check)
- Search by name or CPF
- LGPD notification consent flag — controls whether automated messages are sent

### Service Management
- Create, edit, delete services
- Custom duration (30 min, 45 min, 60 min, 90 min, 120 min, etc.)
- Bind services to specific professionals

### Appointment System
- Interactive calendar with weekly/monthly/daily views
- Click a time slot to open the booking form
- Automatic conflict detection — overlapping appointments are blocked
- Appointment lifecycle: `confirmed` → `completed` or `no-show`
- Owners can mark appointments as completed or no-show from the calendar
- Delete appointments directly from the calendar

### Multi-professional Support
- Business owners invite professionals to their account
- Each professional has their own working hours and service list
- Professional portal: own agenda (`MyAgenda`), own availability (`MyAvailability`), own services (`MyServices`)
- Professionals can only see and manage their own appointments

### Working Hours & Time Blocks
- Configure available hours per day of week for each professional
- Block specific time ranges (holidays, breaks, personal time)
- Booking page only shows available slots respecting working hours and blocks

### Public Booking Page
- Each business gets a unique shareable URL: `/agendar/{slug}`
- Clients book without creating an account
- Client fills name, birth date, CPF, phone, email, chooses service, professional, date and time
- LGPD consent checkbox at booking time
- Rate-limited per IP to prevent spam

### Client Self-Manage Link
- Each booking generates a unique public token URL: `/agendamento/{token}`
- Client can cancel or reschedule their own appointment
- 24-hour cancellation rule: cancellations less than 24 hours before the appointment are blocked

### Notifications (WhatsApp-first with e-mail fallback)
- Booking confirmation sent immediately after scheduling
- 24-hour automated reminder before the appointment
- **Fallback chain** (not broadcast): WhatsApp is tried first; if it fails or is not configured, e-mail is tried next; chain stops at the first successful delivery
- Each delivery attempt is audit-logged with its outcome: `sent`, `skipped_not_configured`, or `failed`
- Consent gate: clients who opted out receive no notifications; skips are logged for LGPD compliance
- WhatsApp supports Evolution API, Z-API, and generic providers (configurable via env vars)

### Automated Reminders
- In-process scheduler sends reminders 24 hours before each appointment
- Idempotent: each appointment is reminded at most once (`reminder_sent_at` column)
- Can also be triggered via cron job (`python -m app.jobs.send_reminders`)

### Post-appointment Reviews
- Clients can leave a star rating and comment after their appointment
- Reviews are visible on the business dashboard

### Dashboard & Analytics
- Total appointments, completed, no-shows, cancellations, revenue
- No-show rate, cancellation rate, realization rate (% of scheduled that completed)
- Period-over-period comparison (current vs previous period)
- Export as **PDF** (formatted report via WeasyPrint) or **CSV**
- Revenue and appointment count charts

### Staff Management
- Owner can add, view, and remove staff (other professionals)
- Roles and access are enforced on every protected endpoint

### Infrastructure
- Docker + Docker Compose — one command to run the full stack (PostgreSQL + API + frontend)
- Alembic migrations run automatically on container startup
- Health check endpoint (`GET /health`)
- GitHub Actions CI — runs the full test suite on every push
- SQLite fallback for zero-config local development

---

## Getting Started

### Run with Docker (recommended)

```bash
# generate a secret key and export it
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

docker compose up --build
```

- Frontend: http://localhost:8080
- API: http://localhost:8000
- Health: http://localhost:8000/health

Migrations run automatically on startup.

---

### Backend — local setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set at minimum `SECRET_KEY` (generate with `python3 -c "import secrets; print(secrets.token_hex(32))"`).

Apply migrations and start:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000

#### PostgreSQL (dev & production)

Set `DATABASE_URL` in `.env`:

```
DATABASE_URL=postgresql+psycopg2://scheduling:scheduling@localhost:5432/scheduling
```

Start a local Postgres instance:

```bash
docker compose up -d db
```

#### Email

Set `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_USE_TLS` in `.env`.
If `SMTP_HOST` is empty, emails are logged to stdout instead of sent.

#### WhatsApp

| Variable | Description |
|---|---|
| `WHATSAPP_API_URL` | Provider endpoint |
| `WHATSAPP_PROVIDER` | `evolution`, `zapi`, or `generic` |
| `WHATSAPP_API_TOKEN` | API key / bearer token |
| `WHATSAPP_CLIENT_TOKEN` | Z-API client token (Z-API only) |

If `WHATSAPP_API_URL` is empty, WhatsApp messages are logged to stdout and the service falls back to e-mail.

#### Reminders

| Variable | Default | Description |
|---|---|---|
| `REMINDERS_ENABLED` | `false` | Enable the in-process reminder scheduler |
| `REMINDER_HOURS_BEFORE` | `24` | How many hours before to send the reminder |
| `REMINDER_INTERVAL_MINUTES` | `15` | How often the scheduler checks for due reminders |

For production, prefer the cron job over the in-process scheduler to avoid duplicate sends across instances:

```bash
python -m app.jobs.send_reminders
```

#### Other

| Variable | Default | Description |
|---|---|---|
| `FRONTEND_URL` | `http://localhost:5173` | Base URL for links in notifications |
| `SECRET_KEY` | — | JWT signing key (required) |

---

### Running tests

```bash
cd backend
pytest
```

The test suite uses SQLite by default. To run against PostgreSQL, set `DATABASE_URL` before running.

#### Lint

```bash
ruff check app tests
```

---

### Frontend — local setup

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

---

### Creating a new migration

```bash
cd backend
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

---

## Project Structure

```
service-scheduling-api/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── channels/          # Notification channel implementations
│   │   │   │   ├── email_channel.py
│   │   │   │   ├── whatsapp_channel.py
│   │   │   │   └── log_channel.py
│   │   │   ├── notification_channel.py  # NotificationChannel ABC + Notification dataclass
│   │   │   ├── notifications.py   # NotificationService (fallback chain)
│   │   │   ├── reminders.py       # Reminder scheduler
│   │   │   ├── report/            # PDF and CSV export
│   │   │   ├── email.py
│   │   │   ├── whatsapp.py
│   │   │   ├── scheduling.py      # Conflict detection
│   │   │   ├── security.py        # JWT + password hashing
│   │   │   └── working_hours.py
│   │   ├── models/
│   │   │   ├── appointment.py
│   │   │   ├── client.py
│   │   │   ├── notification_log.py
│   │   │   ├── professional.py
│   │   │   ├── review.py
│   │   │   ├── service.py
│   │   │   ├── time_block.py
│   │   │   ├── user.py
│   │   │   └── working_hours.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── appointment.py
│   │   │   ├── client.py
│   │   │   ├── dashboard.py
│   │   │   ├── manage.py          # Public self-manage link
│   │   │   ├── professional.py
│   │   │   ├── public.py          # Public booking page
│   │   │   ├── review.py
│   │   │   ├── service.py
│   │   │   ├── settings.py
│   │   │   ├── staff.py
│   │   │   └── time_block.py
│   │   └── main.py
│   ├── alembic/                   # Database migrations
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Appointments.jsx
│   │   │   ├── Clients.jsx
│   │   │   ├── Services.jsx
│   │   │   ├── Professionals.jsx
│   │   │   ├── WorkingHours.jsx
│   │   │   ├── Staff.jsx
│   │   │   ├── Reviews.jsx
│   │   │   ├── Settings.jsx
│   │   │   ├── PublicBooking.jsx
│   │   │   ├── ManageAppointment.jsx
│   │   │   ├── MyAgenda.jsx       # Professional portal
│   │   │   ├── MyAvailability.jsx
│   │   │   ├── MyServices.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── ForgotPassword.jsx
│   │   │   └── ResetPassword.jsx
│   │   └── components/
└── docker-compose.yml
```

---

## Notification Channel Architecture

The notification system uses a **fallback chain**, not broadcast. Channels are tried in priority order and the chain stops at the first successful delivery.

Default order: **WhatsApp → E-mail**

To add a new channel, implement `NotificationChannel`:

```python
from app.core.notification_channel import Notification, NotificationChannel

class SMSChannel(NotificationChannel):
    name = "sms"

    def send(self, notification: Notification) -> bool:
        # return True  → delivered, chain stops
        # return False → not configured/no recipient, next channel is tried
        # raise        → delivery failed, next channel is tried, logged as "failed"
        ...
```

Then include it in `_default_service()` in `app/core/notifications.py`:

```python
return NotificationService([WhatsAppChannel(), SMSChannel(), EmailChannel()])
```

Every delivery attempt is recorded in `notification_logs` with its channel, outcome, and appointment ID.

---

## Author

Developed by Amanda Nanni.
