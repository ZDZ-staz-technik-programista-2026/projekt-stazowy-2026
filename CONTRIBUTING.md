# Contributing Guide

This is an **educational internship project**. We work the way real software teams do:
everything goes through **branches and pull requests (PRs)**, and a teammate reviews
your code before it is merged. Follow this guide and you will practise exactly the
workflow used in professional IT teams.

> **The golden rule:** never push directly to `main`. All changes go through a Pull Request.

---

## 1. Before you start

1. Make sure you have access to the repository (role: **Write**).
2. Read the `README.md` for the project description and how to run the app.
3. Pick up your task on the **Jira** board and move it to *In Progress*.

## 2. Branching model

- `main` is **protected** and must always work. You cannot commit to it directly.
- Create a **feature branch** for every task.

**Branch naming** (lowercase, words separated by `-`), prefix by type:

| Prefix | Use for | Example |
|---|---|---|
| `feature/` | new functionality | `feature/kanban-board` |
| `fix/` | bug fixes | `fix/login-validation` |
| `docs/` | documentation only | `docs/setup-instructions` |
| `chore/` | tooling, config, cleanup | `chore/add-eslint` |

If your task has a Jira key, put it in the branch name: `feature/PROJ-12-task-form`.

```bash
git switch main
git pull                 # get the latest main
git switch -c feature/PROJ-12-task-form
```

## 3. Commits

- Commit **small and often**. One logical change per commit.
- Write clear messages in the **imperative mood**: `Add task status filter`, not `added filters`.
- Optional but encouraged — prefix the type: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.

```bash
git add .
git commit -m "feat: add task status filter"
git push -u origin feature/PROJ-12-task-form
```

## 4. Opening a Pull Request

1. Push your branch and open a **Pull Request** into `main`.
2. Fill in the PR template (summary, related Jira issue, how you tested it).
3. **Request a review from a teammate.** Remember: GitHub does not let you approve
   your own PR — that is on purpose, so someone else always looks at the code.
4. Keep PRs **small** — easier and faster to review than a huge one.

## 5. Reviewing a teammate's PR

Reviewing is a core skill, not a formality. When you review:

- Read the code and check it does what the PR says.
- Be **specific and kind** — comment on the code, not the person.
- Ask questions if something is unclear; suggest, don't demand.
- Use **Approve** when it's good, or **Request changes** if something must be fixed.

## 6. Merging (publishing your code)

A PR can be merged when:

- it has **at least 1 approval** from a teammate,
- all review **conversations are resolved**,
- there are no requested changes left open.

Then the **author** clicks **Merge** — you publish your own code. The feature branch
is deleted automatically. Pull the updated `main` before starting your next task.

## 7. Data & security rules (from the internship regulations)

- Work **only on test / fake data**. No real personal or client data — ever
  (regulations §2–3, §8, §10).
- **Never commit secrets** (passwords, API keys, tokens). Keep them in `.env`,
  which is git-ignored; commit a `.env.example` with placeholder values instead.
- **AI tools** are for help and learning only (explaining, suggesting). Do not paste
  confidential, client, or personal data into them, and always understand and test
  any code they produce (regulations §9).

---

Questions? Ask on **Slack** or raise it at the daily stand-up. When in doubt, ask early.
