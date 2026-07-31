# What does this change?

This change updates the README licence section to match the actual licence included in the repository.  
The previous TODO statement incorrectly said that the repository had no licence assigned, even though the MIT LICENSE file already exists.  
The README now states that the project is licensed under the MIT License and clarifies that third-party dependencies and assets may have their own licences.

## Related Jira task

KAN-70

## Type of change

- [ ] New feature (`feature/`)
- [ ] Bug fix (`fix/`)
- [x] Documentation (`docs/`)
- [ ] Refactoring — no behaviour change (`refactor/`)
- [ ] Tests (`test/`)

## How to verify it

1. Open `README.md`
2. Navigate to the "Licence" section
3. Confirm that it states the project is licensed under the MIT License and no longer contains the outdated TODO message

## Screenshots

not applicable

---

## Author checklist

- [x] The code runs locally (both frontend and backend start without errors)
- [x] The branch follows the naming convention (`feature/`, `fix/`, ...)
- [x] Commit messages are descriptive and written in the imperative mood
- [x] I am not committing the database file, `node_modules/`, `venv/` or `.env`
- [x] There is **no real personal data** in the code or in the test fixtures
- [x] **I understand every line in this pull request** and can explain it during review
      (this includes anything written with the help of an AI assistant)
- [x] *(from day 14)* The `pytest` suite passes

## Reviewer checklist

- [ ] I read the code and understand what it does
- [ ] I verified the change by following the "How to verify it" steps
- [ ] I asked questions wherever something was unclear
- [ ] All of my comments have been resolved

---

> Reminder: this is an **educational / simulation project** running on **test data only**.
> Merge with **Squash and merge**, after **1 approval** from a teammate.