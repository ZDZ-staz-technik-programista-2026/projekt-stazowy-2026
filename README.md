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
- [Frontend design system (Tailwind v4)](#frontend-design-system-tailwind-v4)
- [Repository structure](#repository-structure)
- [Entry statuses](#entry-statuses)
- [Identity and roles](#identity-and-roles)
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
| Frontend | React + Vite, Tailwind CSS v4 (see [design system](#frontend-design-system-tailwind-v4)) |
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
| Jakub Lewkowicz | Frontend (React), student and supervisor views, Tailwind design tokens, status badge component, accessibility pass |
| Kacper Musiaka | Database, entries API (FastAPI + SQLAlchemy), CSV export, role-scoped reads (soft roles, paired with Jakub on frontend gating), early MySQL portability smoke test |
| Michał Misiewicz | Status state machine, hours validation, tests, deployment, free-tier limits check |

---

## Local setup

> 🔧 **TODO (day 17):** fill this in once the app is built.
> Every step must work on a clean machine — verify this by having a teammate follow it
> **without asking the author any questions**.

### Requirements

- Python 3.11+
- Node.js 20+

### Backend

Navigate to backend directory:
```bash
cd backend
```
#### (If not installed) Create and activate virtual environment and install dependencies:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

##### Note
On macOS/Linux run:
```bash
source .venv/bin/activate
```
instead of:
```bash
.venv\Scripts\activate
```
#### Start FastAPI server:
```bash
uvicorn app.main:app --reload
```
Backend will be available at: http://127.0.0.1:8000/

##### Health check endpoint:
GET http://127.0.0.1:8000/health

Expected response:
{
  "status": "ok"
}

#### Auto-generated API documentation:
http://127.0.0.1:8000/docs

#### To deactivate the virtual environment:
```bash
deactivate
```

### Frontend

The frontend lives in the `frontend/` directory at the root of the repository
(`projekt-stazowy-2026/frontend`): a React application scaffolded with Vite.

Navigate to the frontend directory:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

Start the Vite dev server:
```bash
npm run dev
```

Frontend will be available at: http://127.0.0.1:5173/ (Vite's default dev server port)

Once the backend is running, the auto-generated API documentation is available at `/docs`.

---

## Frontend design system (Tailwind v4)

This project uses **Tailwind CSS v4**, set up via the `@tailwindcss/vite` plugin.

> Note: there is **no** `tailwind.config.js` file. All design tokens live directly in
> `src/index.css` via the `@theme` directive, so this section is the single source of
> truth for token names — use these names, not new ones.

### Setup instructions

1. Install dependencies: `npm install`
2. Run dev server: `npm run dev`

### Design language (utility / status-first)

This is a dense work tool, not a website. Flat surfaces, one accent colour, no shadows.

- **Status colours** (core rule: never colour alone — every status also carries an icon/dot
  and a text label, see [Entry statuses](#entry-statuses)):
  - `draft` (grey): `bg-status-draft-bg` / `text-status-draft-fg`
  - `submitted` (blue): `bg-status-submitted-bg` / `text-status-submitted-fg`
  - `approved` (green): `bg-status-approved-bg` / `text-status-approved-fg`
  - `needs_revision` (amber, **not red** — it's a request, not an error): `bg-status-revision-bg` / `text-status-revision-fg`
- **Typography:**
  - **Scale:** limited to `text-xs` (12px), `text-sm` (13px), `text-base` (15px), `text-lg` (18px), `text-xl` (24px).
  - **Weights:** use only `font-regular` (400) or `font-medium` (500).
  - **Numbers:** times and hour counts must use `font-mono` so digits align in columns.
- **Radii & borders:**
  - Controls (buttons/inputs): `rounded-control` (8px).
  - Cards: `rounded-card` (12px).
  - Borders are always 1px (`border` with the `border-border` colour).
  - **No shadows allowed.**

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

Every status is rendered with a shared status badge component: a dot/icon **and** a text
label together, never colour alone, meeting WCAG AA contrast and staying readable in a
black-and-white printout.

---

## Identity and roles

**Decision: soft roles, no passwords.**

- A selector lets the user pick a current identity: one of the fictional students, or the
  supervisor. There is no login step — the identity is kept in application state only.
- With a student identity active, the backend enforces the scope server-side, so a student
  can only see and edit their own entries. A student identity cannot open the supervisor
  queue; the supervisor identity can.
- **Known limitation:** this is *soft* authorisation — there are no passwords, sessions or
  hashing, so it is not a barrier against a determined user calling the API directly. It is
  acceptable here because the data is fictional and the app never replaces the official ZDZ
  journal.
- Real password authentication (hashing, sessions) is explicitly **out of MVP**. It stays a
  candidate only behind a formal change request stating its cost and what it displaces — see
  [MVP scope](#mvp-scope).

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

**Decision: SQLite locally, with an early MySQL portability check.** Daily development and
the pytest suite stay on SQLite for all three developers; nothing about day-to-day work
changes.

- **Day 16:** free-tier limits (storage, inactivity policy) on Render and Aiven are checked
  first, moved earlier so there are no surprises later.
- **Day 16:** the Aiven MySQL instance is provisioned early and the app plus a slice of the
  pytest suite run against it once, purely to confirm the models are portable. This instance
  is reused for the later migration.
- **Day 18:** the same instance is switched over for the production deployment, type
  differences (dates, Boolean, autoincrement) are re-checked, and Kacper runs the MySQL
  workshop for the rest of the team — this stays the database knowledge-transfer step.

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

- [ ] Identity and role selector — soft roles, no passwords: pick a fictional student or the
      supervisor; the backend enforces that a student sees only their own entries
- [ ] Entry CRUD: date, start and end time, work description, blockers
- [ ] Worked hours computed automatically from the time range
- [ ] Status state machine (see table above)
- [ ] Return an entry with a mandatory comment (supervisor view)
- [ ] Data privacy: students can only see and edit their own entries (enforced server-side)
- [ ] Student view (own journal) and supervisor view (approval queue for all students)
- [ ] Daily, weekly and overlap validation
- [ ] Permanent "DEMO — test data" banner in the UI

### Optional features (only with spare capacity, in this order)

1. Weekly statistics — backend and frontend (total hours, entry count, % approved)
2. Remaining-capacity notice — **build at most one**: a weekly progress bar *or* a lighter
   daily hours counter
3. Filtering entries by date and status
4. CSV export / print view
5. Docker containerisation of the backend

### Out of MVP — requires a change request

- **Real password authentication:** login, sessions, password hashing. The soft-role
  selector above already covers the MVP's privacy needs; this is the security-grade version
  and lands only behind an explicit change request stating its cost in hours and the stories
  it displaces.

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

> 🔧 **TODO (day 18):** choosing the project licence is an internship task
> (learning area 15: copyright and software licensing).
> Until then this repository has no licence assigned.

---

## Language conventions

Everything in this repository is written in **English**: code, file names, branch names,
commit messages, pull request descriptions, code review comments, documentation and the
application UI.

The formal internship paperwork (programme, regulations, journal, attendance sheets) is kept
**in Polish**, outside this repository — it is not part of the codebase.
