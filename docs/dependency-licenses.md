# Dependency Licences

Repository chosen licence: **MIT License** (selected in KAN-70)

This document lists the main direct backend and frontend dependencies,
their versions and licences. The purpose is to verify that external
dependencies are compatible with the project's MIT License.

Repository path:
`docs/dependency-licenses.md`

---

## Backend dependencies

| Dependency        | Version | Licence                    | Compatibility with MIT                                                                                                                                                                                                    |
| ----------------- | ------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| httpx2            | 2.9.1   | BSD-3-Clause               | Compatible. BSD-3-Clause is a permissive licence and allows use, modification and distribution with licence notice preservation.                                                                                          |
| FastAPI           | 0.139.0 | MIT                        | Compatible. Uses the same permissive MIT licence terms.                                                                                                                                                                   |
| Uvicorn           | 0.51.0  | BSD-3-Clause               | Compatible. BSD-3-Clause does not restrict MIT licensed projects.                                                                                                                                                         |
| SQLAlchemy        | 2.0.51  | MIT                        | Compatible. Uses the same licence type.                                                                                                                                                                                   |
| Pydantic          | 2.13.4  | MIT                        | Compatible. Uses the same licence type.                                                                                                                                                                                   |
| pydantic-settings | 2.14.2  | MIT                        | Compatible. Uses the same licence type.                                                                                                                                                                                   |
| python-dotenv     | 1.2.2   | BSD-3-Clause               | Compatible. Permissive licence with notice requirements.                                                                                                                                                                  |
| pytest            | 9.1.1   | MIT                        | Compatible. Uses the same licence type.                                                                                                                                                                                   |
| PyMySQL           | 1.1.1   | MIT                        | Compatible. Uses the same licence type.                                                                                                                                                                                   |
| cryptography      | 44.0.1  | Apache-2.0 OR BSD-3-Clause | Compatible. cryptography is dual-licensed under Apache-2.0 OR BSD-3-Clause. Both licence options are permissive and compatible with MIT projects. The project follows the Apache-2.0 compliance path for this dependency. |

---

## Frontend dependencies

| Dependency                  | Version | Licence | Compatibility with MIT                                  |
| --------------------------- | ------- | ------- | ------------------------------------------------------- |
| @tailwindcss/vite           | 4.3.2   | MIT     | Compatible. Uses the same permissive MIT licence terms. |
| React                       | 19.2.7  | MIT     | Compatible. Uses the same permissive MIT licence terms. |
| React DOM                   | 19.2.7  | MIT     | Compatible. Uses the same permissive MIT licence terms. |
| @eslint/js                  | 10.0.1  | MIT     | Compatible. Uses the same permissive MIT licence terms. |
| @types/react                | 19.2.17 | MIT     | Compatible. Uses the same permissive MIT licence terms. |
| @types/react-dom            | 19.2.3  | MIT     | Compatible. Uses the same permissive MIT licence terms. |
| @vitejs/plugin-react        | 6.0.3   | MIT     | Compatible. Uses the same permissive MIT licence terms. |
| autoprefixer                | 10.5.2  | MIT     | Compatible. Uses the same permissive MIT licence terms. |
| ESLint                      | 10.6.0  | MIT     | Compatible. Uses the same permissive MIT licence terms. |
| eslint-plugin-react-hooks   | 7.1.1   | MIT     | Compatible. Uses the same permissive MIT licence terms. |
| eslint-plugin-react-refresh | 0.5.3   | MIT     | Compatible. Uses the same permissive MIT licence terms. |
| globals                     | 17.7.0  | MIT     | Compatible. Uses the same permissive MIT licence terms. |
| postcss                     | 8.5.19  | MIT     | Compatible. Uses the same permissive MIT licence terms. |
| Tailwind CSS                | 4.3.2   | MIT     | Compatible. Uses the same permissive MIT licence terms. |
| Vite                        | 8.1.1   | MIT     | Compatible. Uses the same permissive MIT licence terms. |

---

## Licence risk assessment

All reviewed dependencies use known permissive open-source licences:

* MIT
* BSD-3-Clause
* Apache-2.0

No unknown, custom, copyleft (for example GPL), or source-available licences were identified.

The `cryptography` dependency version `44.0.1` is an exception to the single-licence entries above because it is dual-licensed under **Apache-2.0 OR BSD-3-Clause**.

Both permitted licensing options are permissive and compatible with the project's MIT License.

For compliance purposes, the project follows the **Apache-2.0 licensing path** for `cryptography==44.0.1`. The project must preserve applicable licence notices and comply with Apache attribution requirements when redistributing this dependency.

No additional mitigation is required.

For BSD-3-Clause dependencies, the project must preserve the original licence
and copyright notices when redistributing those components.

For Apache-2.0 dependencies, including the selected compliance path for
`cryptography==44.0.1`, the project must preserve licence notices and
comply with Apache attribution requirements.

---

## Compatibility conclusion

The project licence selected in KAN-70 is MIT.

All reviewed direct dependencies are compatible with the MIT License.
No dependency licence conflicts were identified.

The dual-licensed `cryptography==44.0.1` dependency is compatible with MIT under either available licence option. The project has selected Apache-2.0 as the compliance path for documentation and redistribution purposes.
