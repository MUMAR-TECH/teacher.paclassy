# Paclassy — AI-Powered School Management Platform

Paclassy is a full-stack Django web application that brings AI capabilities to school management. It provides three distinct portals — for teachers, students, and administrators — each accessible via a simple path-based URL structure on a single domain.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [URL Structure](#url-structure)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Development Setup](#local-development-setup)
  - [Docker Setup](#docker-setup)
- [Environment Variables](#environment-variables)
- [User Roles & Access Control](#user-roles--access-control)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [Deployment](#deployment)

---

## Overview

Paclassy replaces subdomain-based multi-tenancy with a clean, path-based routing model:

| Role    | Base URL            |
|---------|---------------------|
| Teacher | `/teacher/`         |
| Student | `/student/`         |
| Admin   | `/admin_panel/`     |
| API     | `/api/v1/`          |

All three portals share a single Django instance, database, and domain. Role-based access is enforced at both the middleware level (`RolePathMiddleware`) and the view level (`@role_required` decorator).

---

## Features

### Teacher Portal (`/teacher/`)
- **Dashboard** — Overview of classes, students, and recent activity
- **AI Lesson Planner** — Generate lesson plans using Google Gemini AI
- **AI Assessment Generator** — Automatically create assessments and quizzes
- **AI Content Generator** — Produce teaching materials and handouts
- **Teacher AI Agent** — Conversational AI assistant for teachers
- **Attendance Management** — Record and review student attendance
- **Timetable** — View and manage class schedules
- **Student Roster** — Browse and manage assigned students

### Student Portal (`/student/`)
- **Dashboard** — Personalised learning overview
- **AI Tutor** — Interactive AI tutor for guided learning

### Admin Portal (`/admin_panel/`)
- **Dashboard** — School-wide analytics and overview
- **Admin AI Agent** — AI assistant for administrative tasks
- **Student Management** — Enrol, edit, and manage all students
- **Attendance Overview** — School-wide attendance reporting
- **Timetable Management** — Create and edit the school timetable

### Shared / API
- **JWT Authentication** (`/api/v1/auth/`) — Register, login, refresh tokens, logout, and profile
- **Session Login** (`/login/`) — Web-based login that redirects to the appropriate portal
- **REST API** — Full DRF API for AI tools, school management, assessments, and analytics

---

## Architecture

```
┌─────────────────────────────────────────┐
│               Single Domain             │
│          https://yourdomain.com         │
├────────────┬───────────┬────────────────┤
│ /teacher/  │ /student/ │ /admin_panel/  │
│  Teacher   │  Student  │  Admin Portal  │
│  Portal    │  Portal   │                │
├────────────┴───────────┴────────────────┤
│                /api/v1/                 │
│           REST API (JWT Auth)           │
├─────────────────────────────────────────┤
│           Django + PostgreSQL           │
│         Redis (Cache + Celery)          │
│         Google Gemini AI Engine         │
└─────────────────────────────────────────┘
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `RolePathMiddleware` | Redirects authenticated users who access the wrong role's path section to their correct dashboard |
| `@role_required(role)` | View decorator that enforces role-based access; returns 403 for wrong role |
| `TenantMiddleware` | Resolves the active school from the session / user profile |
| JWT (SimpleJWT) | Stateless authentication for the REST API |
| Session Auth | Cookie-based auth for the web portals |
| Celery + Redis | Async task queue (used by AI engine for long-running generation tasks) |

---

## URL Structure

### Public
| URL | Description |
|-----|-------------|
| `GET /` | Home / Login redirect |
| `GET /login/` | Web login page |
| `POST /login/` | Authenticate and redirect to role portal |
| `GET /logout/` | Log out and redirect to `/login/` |
| `GET /register/` | Registration page |

### Teacher Portal
| URL | Description |
|-----|-------------|
| `GET /teacher/` | Teacher home (redirects to dashboard) |
| `GET /teacher/dashboard/` | Teacher dashboard |
| `GET /teacher/ai/lesson-planner/` | AI Lesson Planner |
| `GET /teacher/ai/assessment-generator/` | AI Assessment Generator |
| `GET /teacher/ai/content-generator/` | AI Content Generator |
| `GET /teacher/ai/teacher-agent/` | Teacher AI Agent |
| `GET /teacher/school/attendance/` | Attendance management |
| `GET /teacher/school/timetable/` | Timetable view |
| `GET /teacher/school/students/` | Student roster |
| `GET /teacher/logout/` | Logout |

### Student Portal
| URL | Description |
|-----|-------------|
| `GET /student/` | Student home (redirects to dashboard) |
| `GET /student/dashboard/` | Student dashboard |
| `GET /student/ai/tutor/` | AI Tutor |
| `GET /student/logout/` | Logout |

### Admin Portal
| URL | Description |
|-----|-------------|
| `GET /admin_panel/` | Admin home (redirects to dashboard) |
| `GET /admin_panel/dashboard/` | Admin dashboard |
| `GET /admin_panel/ai/admin-agent/` | Admin AI Agent |
| `GET /admin_panel/school/students/` | Student management |
| `GET /admin_panel/school/attendance/` | Attendance overview |
| `GET /admin_panel/school/timetable/` | Timetable management |
| `GET /admin_panel/logout/` | Logout |

### REST API (`/api/v1/`)
| URL | Method | Description |
|-----|--------|-------------|
| `/api/v1/auth/register/` | POST | Register a new user |
| `/api/v1/auth/login/` | POST | Obtain JWT access + refresh tokens |
| `/api/v1/auth/refresh/` | POST | Refresh access token |
| `/api/v1/auth/logout/` | POST | Blacklist refresh token |
| `/api/v1/auth/me/` | GET/PATCH | Get or update current user profile |
| `/api/v1/schools/` | GET/POST | School management |
| `/api/v1/ai/` | — | AI engine endpoints |
| `/api/v1/assessments/` | — | Assessment endpoints |
| `/api/v1/school-mgmt/` | — | School management endpoints |
| `/api/v1/analytics/` | — | Analytics endpoints |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6, Django REST Framework |
| Auth | SimpleJWT (API), Django Sessions (web) |
| Database | PostgreSQL (production), SQLite (development) |
| Cache / Queue | Redis, Celery |
| AI | Google Gemini (`gemini-1.5-flash`) |
| Frontend | Django templates, Tailwind CSS (CDN), Alpine.js |
| Web Server | Gunicorn + Nginx |
| Container | Docker, Docker Compose |

---

## Project Structure

```
teacher.paclassy/
├── apps/
│   ├── accounts/          # User model, auth views, middleware, decorators
│   ├── adminpanel/        # Admin portal views and URLs
│   ├── ai_engine/         # Google Gemini integration, AI views
│   ├── analytics/         # Analytics models and API
│   ├── assessments/       # Assessment models and API
│   ├── dashboard/         # Dashboard templates
│   ├── school_mgmt/       # School management (attendance, timetable)
│   ├── schools/           # School model, tenant middleware
│   ├── student/           # Student portal views and URLs
│   └── teacher/           # Teacher portal views and URLs
├── paclassy/
│   ├── settings/
│   │   ├── base.py        # Shared settings
│   │   ├── development.py # Dev overrides (SQLite, console email)
│   │   └── production.py  # Production overrides
│   ├── urls.py            # Root URL configuration
│   ├── api_urls.py        # API URL routing
│   ├── web_urls.py        # Web/session URL routing
│   ├── celery.py          # Celery configuration
│   ├── asgi.py
│   └── wsgi.py
├── templates/
│   ├── accounts/          # Login, register templates
│   ├── adminpanel/        # Admin portal templates + base.html
│   ├── student/           # Student portal templates + base.html
│   └── teacher/           # Teacher portal templates + base.html
├── static/
│   └── js/                # app.js, ai_features.js, dark_mode.js
├── nginx/
│   └── nginx.conf         # Nginx reverse proxy config
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements.txt
└── .env.example
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip
- Redis (for cache and Celery)
- PostgreSQL (for production) or SQLite (for development)
- A Google Gemini API key (for AI features)

### Local Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/MUMAR-TECH/teacher.paclassy.git
   cd teacher.paclassy
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env and fill in your values
   ```

5. **Run database migrations**

   ```bash
   python manage.py migrate --settings=paclassy.settings.development
   ```

6. **Create a superuser**

   ```bash
   python manage.py createsuperuser --settings=paclassy.settings.development
   ```

7. **Collect static files**

   ```bash
   python manage.py collectstatic --settings=paclassy.settings.development
   ```

8. **Start the development server**

   ```bash
   python manage.py runserver --settings=paclassy.settings.development
   ```

9. **Start Celery worker** (optional, required for AI features)

   ```bash
   celery -A paclassy worker -l info
   ```

Visit `http://localhost:8000/` and log in. After login you will be redirected to the appropriate portal based on your role.

### Docker Setup

1. **Copy and configure environment**

   ```bash
   cp .env.example .env
   # Edit .env — set DEBUG=False, fill in DATABASE_URL, SECRET_KEY, GEMINI_API_KEY
   ```

2. **Build and start all services**

   ```bash
   docker compose up --build
   ```

3. **Run migrations inside the container**

   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   docker compose exec web python manage.py collectstatic --no-input
   ```

The application is now accessible at `http://localhost/`.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | — | Django secret key (use a long random string in production) |
| `DEBUG` | No | `False` | Set to `True` for development |
| `ALLOWED_HOSTS` | Yes | `localhost 127.0.0.1` | Space-separated list of allowed hostnames |
| `DATABASE_URL` | No | SQLite | PostgreSQL connection URL, e.g. `postgresql://user:pass@db:5432/paclassy` |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis URL for cache and Celery broker |
| `GEMINI_API_KEY` | Yes (AI features) | — | Google Gemini API key |
| `GEMINI_MODEL` | No | `gemini-1.5-flash` | Gemini model name |

---

## User Roles & Access Control

Paclassy uses a three-role model stored on the `User` model:

| Role | Value | Portal |
|------|-------|--------|
| Teacher | `teacher` | `/teacher/` |
| Student | `student` | `/student/` |
| Admin | `admin` | `/admin_panel/` |

### How access control works

1. **`RolePathMiddleware`** — Runs on every request. If an authenticated user accesses a path that belongs to a different role (e.g. a student visits `/teacher/dashboard/`), they are transparently redirected to their own dashboard.

2. **`@role_required(role)` decorator** — Applied to every view in the role portals. Returns `403 Forbidden` if the user's role does not match the required role. This is the final enforcement layer.

3. **Login redirect** — After a successful web login, the user is redirected to their correct portal dashboard automatically.

### Creating users with specific roles

Via Django admin (`/admin/`) or the REST API (`POST /api/v1/auth/register/`):

```json
{
  "username": "john.doe",
  "email": "john@school.com",
  "password": "securepassword",
  "role": "teacher"
}
```

---

## API Reference

All API endpoints are under `/api/v1/` and require a JWT `Authorization: Bearer <token>` header unless noted.

### Authentication

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@school.com","password":"pass1234","role":"teacher"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"pass1234"}'

# Response contains { "access": "...", "refresh": "...", "user": {...} }

# Refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'

# Logout (blacklist refresh token)
curl -X POST http://localhost:8000/api/v1/auth/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'

# Get/update profile
curl http://localhost:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer <access_token>"
```

---

## Running Tests

```bash
# Run all tests
python manage.py test --settings=paclassy.settings.development

# Run role isolation tests only
python manage.py test apps.accounts.tests_role_isolation --settings=paclassy.settings.development --verbosity=2
```

The role isolation test suite (`apps/accounts/tests_role_isolation.py`) covers:
- Unauthenticated access is redirected to login for all portals
- Each role can access their own dashboard
- Teachers cannot access student or admin routes
- Students cannot access teacher or admin routes
- Admins cannot access teacher or student routes
- Login redirects to the correct portal for each role

---

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Set a strong, unique `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to your domain(s)
- [ ] Set `DATABASE_URL` to your PostgreSQL connection string
- [ ] Set `REDIS_URL` to your Redis instance
- [ ] Set `GEMINI_API_KEY`
- [ ] Run `python manage.py collectstatic`
- [ ] Run `python manage.py migrate`
- [ ] Use Gunicorn behind Nginx (see `docker-compose.yml` and `nginx/nginx.conf`)
- [ ] Configure HTTPS / TLS termination at Nginx or load balancer

### Docker Compose (Production)

The included `docker-compose.yml` starts:
- `web` — Gunicorn Django application
- `celery` — Celery worker for async AI tasks
- `db` — PostgreSQL 17
- `redis` — Redis 7
- `nginx` — Nginx reverse proxy serving static/media files

```bash
docker compose up -d
```

---

## License

This project is proprietary software owned by MUMAR-TECH.
