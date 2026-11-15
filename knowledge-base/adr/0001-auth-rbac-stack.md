# ADR 0001 — Authentication and RBAC Stack for the ERP

- **Status:** Accepted
- **Date:** 2026-11-15
- **Decision owner:** Product owner / developer (solo maintainer)
- **Scope:** Backend ERP, Authentication and Authorization layer
- **Related branch:** `spike/auth-poc`
- **Related issue:** https://github.com/AirPart/airpart-backend/issues/84

---

## 1. Context

This project is a **single, internal ERP** for a company that sells aircraft parts. It has three primary business domains:

1. **Human Resources (HR)** — employees, attendance, contracts, payroll.
2. **Financial reporting** — invoices, receipts/payments, profit and loss, periodic reports.
3. **Product sales** — parts catalogue, customers, orders, quotations.

Real constraints of the project:

- The team is **solo-maintained**; every extra hour of work directly delays delivery.
- The developer's **primary language is Python**.
- Phase one deployment is **Docker on a manually managed server**; **CI/CD and automation** follow later.
- The domain is **CRUD-heavy with reporting**, not real-time and not high-traffic.
- Local requirements: Jalali (Persian) calendar, RTL, IRR currency, and possibly a payment gateway.
- The system must **live and be maintained for years**, so version stability and LTS matter.
- Access control starts with **simple roles** but will very likely grow into **domain-scoped** (branch/department) and **object-level** permissions (for example, "only my own invoices").

Goal of this ADR: choose the authentication and access-control stack **before writing any authentication code**, in a documented and reviewable way.

### Separating two decisions

It is important that these two choices are evaluated separately and not conflated:

| Layer                    | Responsibility                                                               | Candidates                                                |
| ------------------------ | ---------------------------------------------------------------------------- | --------------------------------------------------------- |
| **Authentication**       | Identifying the user, issuing and validating tokens, future OAuth/OIDC flows | SimpleJWT, Authlib, Passport                              |
| **Authorization / RBAC** | Deciding "who may do what on which object"                                   | Django permissions, django-guardian, django-rules, Casbin |

> **Key point:** `Authlib` is **not** an RBAC engine. It handles OAuth2/OIDC and JWT/JWS/JWE. Any candidate presented with Authlib must be paired with a separate policy engine (Casbin, oso, or a hand-rolled layer) to be assessed for RBAC. This ADR respects that separation.

---

## 2. Decision Drivers

| #   | Decision driver                                             | Weight |
| --- | ----------------------------------------------------------- | ------ |
| D1  | Long-term maintenance cost for a single person              | 25%    |
| D2  | RBAC maturity and support for domain/object-level access    | 20%    |
| D3  | Ecosystem (reporting, Excel/PDF, Jalali calendar, payments) | 20%    |
| D4  | Learning curve given a Python background                    | 15%    |
| D5  | Type safety and confidence when refactoring                 | 10%    |
| D6  | Long-term support and release stability (LTS)               | 10%    |

The weights are deliberate: for a solo-maintained administrative ERP, **maintenance cost** and **ecosystem** matter more than raw throughput.

---

## 3. Options Considered

### Option A — Django 5.2 LTS + DRF + SimpleJWT + Casbin

- **Authentication:** `djangorestframework-simplejwt` (access/refresh)
- **Authorization:** built-in Django permissions for the admin panel + `django-guardian` or `django-rules` for object-level + `casbin-django-orm-adapter` for domain-scoped policy
- **Strengths:** ready-made admin panel, mature ORM and migrations, strong reporting ecosystem, LTS until April 2028, established Iranian packages (Jalali calendar, payments)
- **Weaknesses:** weak type safety in the ORM, partial async support, heavier than FastAPI for a pure API

### Option B — FastAPI + Authlib + Casbin

- **Authentication:** Authlib (JWT/OAuth2) or hand-rolled JWT
- **Authorization:** Casbin with a SQLAlchemy adapter (or an async adapter)
- **Strengths:** fast start, Pydantic v2, automatic OpenAPI, real async, high performance
- **Weaknesses:** no admin, no built-in migrations, no permission framework; everything is hand-built. `fastapi-users` has been in **maintenance mode** since October 2025 and receives no new features.

### Option C — Go + Casbin

- **Authentication:** hand-rolled JWT or `golang-jwt`
- **Authorization:** Casbin (an Apache Software Foundation project)
- **Strengths:** the most mature policy engine, genuine type safety, single binary, low runtime and ops cost
- **Weaknesses:** a new language for the team, heavy boilerplate, no ready-made admin/ORM, a weaker ecosystem for financial reporting and Persian Excel/PDF output

### Option D — NestJS + Passport (+ CASL/Casbin) — **screened out**

- **Reason for rejection:** the developer's primary language is Python. Adding a second runtime (Node.js) to a solo-maintained ERP raises ops cost and cognitive load without proportionate benefit. This option was **not fully evaluated** and is not included in the scoring table; it is recorded only as a discarded alternative.

---

## 4. Comparison

Scores range from 1 (poor) to 5 (excellent). Weighted score = Σ(weight × score).

| Criterion                      | Weight | A: Django + DRF | B: FastAPI + Authlib/Casbin | C: Go + Casbin |
| ------------------------------ | ------ | --------------- | --------------------------- | -------------- |
| Maintenance cost (D1)          | 25%    | **5**           | 3                           | 4              |
| RBAC maturity (D2)             | 20%    | 4               | 3                           | **5**          |
| Reporting/local ecosystem (D3) | 20%    | **5**           | 4                           | 3              |
| Learning curve (D4)            | 15%    | 4               | 4                           | 1              |
| Type safety (D5)               | 10%    | 2               | 4                           | **5**          |
| Long-term support (D6)         | 10%    | **5**           | 4                           | **5**          |
| **Weighted score**             | 100%   | **4.35**        | 3.55                        | 3.75           |

### Notes on the key scores

- **Maintenance cost:** Django scores highest because it ships with admin, migrations, forms, permissions, and a panel. FastAPI scores lowest because every layer must be built and maintained, and one of its main auth packages (fastapi-users) is in maintenance mode.
- **RBAC maturity:** Go/Casbin scores highest (native, mature Casbin). Django ranks second through the combination of built-in permissions + guardian + the Casbin adapter. FastAPI is third for lack of a ready-made layer.
- **Type safety:** Go wins; Django with a dynamic ORM is the weakest.
- **LTS:** Django 5.2 LTS receives security support until **April 2028**; Go has its 1.x compatibility promise and Casbin sits under the Apache umbrella; FastAPI is active but has no formal LTS.

---

## 5. Decision

**Option A is selected:**

> **Django 5.2 LTS + Django REST Framework + SimpleJWT + Casbin (with the Django adapter)**

### Proposed access-control architecture

1. **Authentication:** JWT with a short-lived access token and rotating refresh token, via SimpleJWT.
2. **Baseline permissions (admin):** built-in Django permissions for the admin panel.
3. **Business permissions (primary RBAC):** Casbin with the `sub, dom, obj, act` model
   - `sub` = user or role
   - `dom` = domain (branch / department)
   - `obj` = resource (`invoice`, `employee`, `part`)
   - `act` = action (`read`, `write`, `approve`)
4. **Object-level:** for cases such as "only my own invoices", use `django-guardian` or an additional condition in the policy.

This model is implemented from day one so that when the company grows and branches/departments are added, the access layer does not need to be rewritten.

---

## 6. Consequences

### Positive

- High delivery speed for the administrative domain (HR, invoices, reports).
- A ready-made admin panel removes the initial cost of building CRUD screens.
- Financial reporting is straightforward with the ORM and Excel/PDF export.
- A clear LTS through 2028, suitable for a long-lived ERP.
- Simple Docker and CI/CD: `web` container plus the database chosen in ADR 0002 ( and Redis once background jobs arrive ), with `migrate` in the entrypoint.
- A growth path for RBAC from simple roles to domain-scoped access without changing the stack.

### Negative / Risks

- **Weak type safety:** mitigated with `mypy` + `django-stubs` and `pytest-django` tests.
- **Limited async:** heavy reports run through Celery + Redis rather than pure async.
- **Casbin in Python:** the Django adapter is moderately maintained; versions must be pinned and policy tests must run in CI.
- **SimpleJWT:** maintenance activity is low; pin the version and review CVEs periodically. If needed, replace it with a lightweight JWT implementation or Authlib.

### Risk mitigations

- Pin versions in `pyproject.toml` / `requirements.txt`.
- Run policy tests in CI (`pytest` plus `model.conf` and `policy.csv` fixtures).
- Run a monthly dependency security audit (`pip-audit`).
- Document policies under `knowledge-base/` so access-control decisions remain reviewable.

---

## 7. Rejected Options

| Option                                | Reason for rejection                                                                                                                                                                                                                                                                                                 |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **FastAPI + Authlib + Casbin**        | Good time-to-start, but no admin, migrations, permission framework, or stable auth package; maintenance cost is high for a solo maintainer. `fastapi-users` is in maintenance mode. For this domain (CRUD + reporting), the benefit of raw performance does not offset the cost of building everything from scratch. |
| **Go + Casbin**                       | The cleanest option from an engineering standpoint and the most mature RBAC, but a new language for the team, heavy boilerplate, and no ready ecosystem for financial reporting or Persian Excel/PDF. It would lengthen MVP delivery excessively. Revisit as a future option if a high-traffic service is needed.    |
| **NestJS + Passport (+ CASL/Casbin)** | Screened out: the primary language is Python, and adding a second runtime (Node) to a solo-maintained ERP raises ops cost and cognitive load without justification. Not fully evaluated.                                                                                                                             |
| **Authlib alone as an RBAC solution** | Rejected because Authlib is not an authorization engine; it only provides authentication and tokens. Treating it as an "RBAC stack" is a conceptual error.                                                                                                                                                           |

---

## 8. Proof of Concept

Branch: `spike/auth-poc`

Minimum acceptable PoC scope:

- [ ] `POST /api/auth/login` — issue access and refresh tokens
- [ ] `POST /api/auth/refresh` — rotate the refresh token
- [ ] `GET /api/me` — protected endpoint returning the current user
- [ ] A Casbin model with sample `model.conf` and `policy.csv`
- [ ] One real policy: the `sales` role may only `read` `invoice` within its own domain
- [ ] `pytest` tests for: successful login, failed login, authorized access, unauthorized access (403)
- [ ] `docker-compose.yml` with `web` (database choice in out of scope -- see ADR 0002)
- [ ] `README.md` with run instructions

PoC acceptance criteria: tests pass in CI and the login endpoint works on Docker.

---

## 9. References

### Official documentation

- Django: https://docs.djangoproject.com
- Django 5.2 LTS (supported until April 2028): https://www.djangoproject.com/download/
- Django REST Framework: https://www.django-rest-framework.org
- SimpleJWT: https://django-rest-framework-simplejwt.readthedocs.io
- Casbin: https://casbin.apache.org/docs
- Casbin ecosystem / adapters: https://casbin.apache.org/ecosystem/
- django-guardian: https://django-guardian.readthedocs.io
- django-rules: https://github.com/kalekseev/django-rules
- FastAPI: https://fastapi.tiangolo.com
- Authlib: https://docs.authlib.org
- FastAPI Users (maintenance mode): https://fastapi-users.github.io
- Go: https://go.dev/doc
- sqlc: https://sqlc.dev
- NestJS: https://docs.nestjs.com
- NestJS Passport recipe: https://docs.nestjs.com/recipes/passport
- CASL: https://casl.js.org

### Internal references

- ADR template: `knowledge-base/adr/template.md`
- PoC branch: `spike/auth-poc`

---

## 10. Review Trigger

This decision will be revisited if any of the following occurs:

- A need for a high-traffic API for a mobile app with high concurrency.
- A need for a multi-tenant SaaS with very complex access policies.
- Django LTS or the Casbin Django adapter stops receiving security maintenance.
- The team grows beyond two people and priorities shift toward type safety.
