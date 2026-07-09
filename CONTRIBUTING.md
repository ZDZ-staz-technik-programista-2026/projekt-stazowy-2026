# How we work in this repository

This document applies to the whole team. If something is unclear — **ask early**. Do not stay
blocked for longer than 30 minutes.

---

## 1. The core rule

**Never commit directly to `main`.**

The `main` branch is protected — pushing straight to it will be rejected by GitHub. Every change
reaches `main` through a **pull request** approved by a teammate.

---

## 2. Starting work

```bash
# once
git clone https://github.com/ZDZ-staz-technik-programista-2026/projekt-stazowy-2026.git
cd projekt-stazowy-2026

# before every new task
git checkout main
git pull                              # get the latest state
git checkout -b feature/entry-form    # a new branch for the task
```

### Branch naming

Branches follow the `type/short-description` pattern:

| Type | When | Example |
|---|---|---|
| `feature/` | new functionality | `feature/entry-form` |
| `fix/` | bug fix | `fix/hours-validation` |
| `docs/` | documentation | `docs/readme-setup` |
| `refactor/` | tidying code without changing behaviour | `refactor/entry-service` |
| `test/` | tests | `test/status-transitions` |

One branch = one Jira task.

---

## 3. Commits

- Use the **imperative mood**: `add entry form validation`
- Keep it short and specific — a commit message says **what** changed
- Commit in **small chunks**, not once every three days
- **Push every day** — it is your proof of work (an internship requirement)

```bash
git add .
git commit -m "add entry status transitions"
git push -u origin feature/entry-form
```

**Good messages:**

```
add entry form validation
fix hours calculation for overnight entries
reject overlapping entries for the same student
update readme with setup instructions
```

**Bad messages:**

```
fixes           ← which fixes?
changes         ← what changed?
asdf            ← no
fix             ← fix what?
wip             ← then do not push it to a pull request
```

---

## 4. Pull requests

1. Push your branch to GitHub (`git push`)
2. Open a **pull request** targeting `main`
3. Fill in the template (it appears automatically)
4. Request a review from a teammate (**Reviewers**)
5. Respond to the comments and update the code
6. Once approved: **Squash and merge** → the branch is deleted automatically

### Rules

- **1 approval** from a teammate is required before merging
- Never approve your own pull request
- All comments must be **resolved** before merging
- Keep pull requests **small** — small ones get reviewed properly. If yours touches 30 files,
  it should probably be split

---

## 5. Code review

Reviewing someone else's code is a **separate professional skill**. We practise it deliberately
(day 9, task T-29).

**As a reviewer:**

- read the code and **ask questions** when you do not understand something — a question is not an attack
- comment on the code, not the person: "this function does two things" rather than "you wrote this badly"
- point out what is done well, not only what is wrong
- if everything looks right: **Approve**. If not: **Request changes** with a concrete reason

**As an author:**

- do not get defensive — the review is about the code, not about you
- if you disagree, explain why; disagreeing is allowed
- respond to **every** comment, even with a short "fixed"

---

## 6. Definition of Done

A task is finished when **all** of the following are true:

- [ ] the code runs locally (both frontend and backend start without errors)
- [ ] the pull request has been reviewed and approved by a teammate
- [ ] all pull request comments are resolved
- [ ] the Jira task has been moved to **Done**
- [ ] *(from day 14)* the `pytest` suite passes

---

## 7. What we never commit

Check `.gitignore`, but the essentials are:

- **the database file** (`*.db`, `*.sqlite3`) — everyone has their own local database
- `node_modules/`, `venv/`, `__pycache__/`
- editor settings and OS artefacts (`.DS_Store`)
- `.env` files and any secrets
- **any real personal data** — we work exclusively on fictional data

> If you accidentally push something sensitive — **tell the supervisor immediately**.
> The Git history is public, and a commit that "deletes" a file does not remove it from history.

---

## 8. Language

Everything in this repository is written in **English**: code, identifiers, file names, branch
names, commit messages, pull request descriptions, code review comments, documentation and the
application UI.

Spoken communication (stand-ups, client meetings, Slack) stays in Polish. The formal internship
paperwork is in Polish and lives outside this repository.

---

## 9. AI tools

We use **free chat assistants** (ChatGPT, Gemini, Claude) as a learning and coding aid.
We do not use paid or agentic tooling (Copilot, Codex, Claude Code) — none of it is required.

**Rules (internship regulations, § 9):**

- you must **understand**, independently **verify** and **test** any code produced with AI help
- responsibility for the code in a pull request lies with **its author**, not with the chat
- **never paste** confidential information, client data or personal data into an AI tool
- if you cannot explain how your code works during review, it is not ready to be merged

AI is **not a feature of this application** — it is only a working tool.

---

## 10. Project character

This is an **educational / simulation project**. We work on **test data and fictional students**.
The application does not replace the official internship journal kept for ZDZ.

The internship regulations apply (§ 2–3, § 8, § 9, § 10).
