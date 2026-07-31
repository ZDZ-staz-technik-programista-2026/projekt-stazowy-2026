# Dependency Licences

Repository chosen licence: **MIT License** (selected in KAN-70)

This document lists the main direct backend and frontend dependencies,
their versions and licences. The purpose is to verify that external
dependencies are compatible with the project's MIT License.

Repository path:
`docs/dependency-licenses.md`

---

## Backend dependencies

| Dependency | Version | Licence | Compatibility with MIT |
|---|---|---|---|
| httpx2 | 2.9.1 | BSD-3-Clause | Compatible. BSD-3-Clause is a permissive licence and allows use, modification and distribution with licence notice preservation. |
| FastAPI | 0.139.0 | MIT | Compatible. Uses the same permissive MIT licence terms. |
| Uvicorn | 0.51.0 | BSD-3-Clause | Compatible. BSD-3-Clause does not restrict MIT licensed projects. |
| SQLAlchemy | 2.0.51 | MIT | Compatible. Uses the same licence type. |
| Pydantic | 2.13.4 | MIT | Compatible. Uses the same licence type. |
| pydantic-settings | 2.14.2 | MIT | Compatible. Uses the same licence type. |
| python-dotenv | 1.2.2 | BSD-3-Clause | Compatible. Permissive licence with notice requirements. |
| pytest | 9.1.1 | MIT | Compatible. Uses the same licence type. |
| PyMySQL | 1.1.1 | MIT | Compatible. Uses the same licence type. |
| cryptography | 44.0.1 | Apache-2.0 | Compatible. Apache-2.0 is permissive and compatible with MIT projects. |

---

## Frontend dependencies

| Dependency | Version | Licence | Compatibility with MIT |
|---|---|---|---|
| @tailwindcss/vite | 4.3.2 | MIT | Compatible. Uses the same licence type. |
| React | 19.2.7 | MIT | Compatible. Uses the same licence type. |
| React DOM | 19.2.7 | MIT | Compatible. Uses the same licence type. |
| @eslint/js | 10.0.1 | MIT | Compatible. Uses the same licence type. |
| @types/react | 19.2.17 | MIT | Compatible. Uses the same licence type. |
| @types/react-dom | 19.2.3 | MIT | Compatible. Uses the same licence type. |
| @vitejs/plugin-react | 6.0.3 | MIT | Compatible. Uses the same licence type. |
| autoprefixer | 10.5.2 | MIT | Compatible. Uses the same licence type. |
| ESLint | 10.6.0 | MIT | Compatible. Uses the same licence type. |
| eslint-plugin-react-hooks | 7.1.1 | MIT | Compatible. Uses the same licence type. |
| eslint-plugin-react-refresh | 0.5.3 | MIT | Compatible. Uses the same licence type. |
| globals | 17.7.0 | MIT | Compatible. Uses the same licence type. |
| postcss | 8.5.19 | MIT | Compatible. Uses the same licence type. |
| Tailwind CSS | 4.3.2 | MIT | Compatible. Uses the same licence type. |
| Vite | 8.1.1 | MIT | Compatible. Uses the same licence type. |

---

## Licence risk assessment

All reviewed dependencies use known permissive open-source licences:

- MIT
- BSD-3-Clause
- Apache-2.0

No unknown, custom, dual, copyleft (for example GPL), or source-available licences were identified.

No additional mitigation is required.

For BSD-3-Clause dependencies, the project must preserve the original licence
and copyright notices when redistributing those components.

For Apache-2.0 dependencies, the project must preserve licence notices and
comply with Apache attribution requirements.

---

## Compatibility conclusion

The project licence selected in KAN-70 is MIT.

All reviewed direct dependencies are compatible with the MIT License.
No dependency licence conflicts were identified.