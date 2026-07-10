# Internship Journal

> ## ⚠️ DEMO PROJECT — TEST DATA ONLY
>
> This application **does not replace** the official internship journal kept for ZDZ.
> It is built as an **educational / simulation project** and runs **exclusively on fictional data**
> ("Test Student 1", "Test Student 2"). We never enter real personal data or real
> internship hours into it.

A web application for daily internship entries: a student creates an entry (date, hours,
work description, blockers) and the supervisor either approves it or returns it for revision.

---

## Table of contents

- [About](#about)
- [Tech stack](#tech-stack)
- [Team and roles](#team-and-roles)
- [Local setup](#local-setup)
- [Repository structure](#repository-structure)
- [Entry statuses](#entry-statuses)
- [Database](#database)
- [Business rules](#business-rules)
- [MVP scope](#mvp-scope)
- [Working with this repository](#working-with-this-repository)
- [Licence](#licence)
- [Language conventions](#language-conventions)

---

## About

Built during a **student internship** for the vocational qualification *technik programista* (351406),
covering the INF.03 and INF.04 qualification units.

| | |
|---|---|
| Dates | 08.07.2026 – 04.08.2026 (20 working days) |
| Host company | PAWEŁ SZMIDT |
| Supervisor / "client" | Paweł Szmidt |
| Organiser | Zakład Doskonalenia Zawodowego w Białymstoku (ZDZ) |
| EU project | „Kształcenie zawodowe na potrzeby Gospodarki 4.0 i GOZ", no. FEPD.08.02-IZ.00-0005/24 |

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | Python + FastAPI |
| Database (local) | SQLite |
| Database (production) | Managed MySQL — Aiven free tier |
| ORM | SQLAlchemy |
| Tests | pytest |
| Demo deployment | Render (backend) / Vercel (frontend) |

---

## Team and roles

| Person | Responsibility |
|---|---|
| Jakub Lewkowicz | Frontend (React), student and supervisor views, styling |
| Kacper Musiaka | Database, entries API (FastAPI + SQLAlchemy), CSV export |
| Michał Misiewicz | Status state machine, hours validation, tests, deployment |

---

## Local setup

> 🔧 **TODO (day 17, task T-36):** fill this in once the app is built.
> Every step must work on a clean machine — verify this by having a teammate follow it
> **without asking the author any questions**.

### Requirements

- Python 3.11+
- Node.js 20+

### Backend

```bash
# TODO: fill in
```

### Frontend

```bash
# TODO: fill in
```

Once the backend is running, the auto-generated API documentation is available at `/docs`.

---

## Repository structure

```
projekt-stazowy-2026/
├── backend/          # FastAPI + SQLAlchemy
│   ├── app/
│   ├── tests/        # pytest
│   └── requirements.txt
└── frontend/         # React + Vite
    ├── src/
    └── package.json
```

> 🔧 **TODO (day 6, tasks T-07 and T-08):** create the `backend/` and `frontend/` directories
> during project setup.

---

## Entry statuses

An entry moves through a small state machine. **Only the transitions below are allowed** —
the backend rejects everything else with `409 Conflict`.

| From | Action | To | Performed by |
|---|---|---|---|
| `draft` | submit for approval | `submitted` | student |
| `submitted` | approve | `approved` | supervisor |
| `submitted` | return with a comment | `needs_revision` | supervisor |
| `needs_revision` | revise and resubmit | `submitted` | student |
| `approved` | — | — | final state |

Returning an entry **without a comment** is not allowed.

---

## Database

We run **two engines**, deliberately:

| Environment | Engine | Why |
|---|---|---|
| Local development | SQLite | Zero configuration. Everyone has their own file, and it is never committed. |
| Production (demo) | Managed MySQL — Aiven free tier | Render's free web services have an **ephemeral filesystem**: any local file, including a SQLite database, is wiped on every redeploy, restart or spin-down. A networked database is the only option. |

SQLAlchemy makes this a change of connection string, not a rewrite — but the models must stay
portable. Do **not** use SQLite-specific column types, and always give string columns an explicit
length, because MySQL requires one and SQLite does not.

The connection string is a **secret**. It lives in environment variables on the host and never
in this repository. `.env` is in `.gitignore`.

> The migration is task T-51, run by Kacper on day 18, and doubles as the database knowledge
> transfer workshop for the rest of the team.

---

## Business rules

All interns on this internship are adults, so the daily limit is a **per-student configuration
field** (`student.daily_hours_limit`, default `8`) rather than something derived from age.

- An entry must not exceed the student's `daily_hours_limit`
- The weekly total must not exceed **40 hours**
- Two entries for the same student **must not overlap** in time
- Adjacent entries are fine: `09:00–12:00` and `12:00–16:00` do **not** overlap
- The entry date must not be in the future; the work description must not be empty

---

## MVP scope

The minimum that must work on **Demo Day (04.08)**:

- [ ] Authentication and roles (Student / Admin login panel)
- [ ] User profiles (basic info: name, role, daily hours limit)
- [ ] Entry CRUD: date, start and end time, work description, blockers
- [ ] Worked hours computed automatically from the time range
- [ ] Status state machine (see table above)
- [ ] Return an entry with a mandatory comment (supervisor view)
- [ ] Data privacy: students can only see and edit their own entries
- [ ] Student view (own journal) and supervisor view (approval queue for all students)
- [ ] Filtering entries by date and status
- [ ] Daily, weekly and overlap validation
- [ ] Permanent "DEMO — test data" banner in the UI

### Optional features (only with spare capacity, in this order)

1. Weekly statistics (total hours, entry count, % approved)
2. Weekly progress bar with a remaining-capacity notice
3. CSV export / print view
4. In-app notifications for returned entries
5. Docker containerisation of the backend

### Optional features (only with spare capacity, in this order)

1. Weekly statistics (total hours, entry count, % approved)
2. CSV export / print view
3. Filtering by date and status
4. Docker
5. Authentication and roles

---

## Working with this repository

Git workflow, branch naming, the pull request process and the Definition of Done:
**[CONTRIBUTING.md](CONTRIBUTING.md)**

The short version:

- never commit directly to `main` — branch protection will reject the push,
- every change lands through a pull request,
- a pull request needs **1 approval** from a teammate.

---

## Licence

> 🔧 **TODO (day 18, task T-39):** choosing the project licence is an internship task
> (learning area 15: copyright and software licensing).
> Until then this repository has no licence assigned.

---

## Language conventions

Everything in this repository is written in **English**: code, file names, branch names,
commit messages, pull request descriptions, code review comments, documentation and the
application UI.

The formal internship paperwork (programme, regulations, journal, attendance sheets) is kept
**in Polish**, outside this repository — it is not part of the codebase.
