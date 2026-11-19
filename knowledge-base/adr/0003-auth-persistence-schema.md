# ADR 0003 — Define Auth and RBAC Persistence Schema

- **Status:** Proposed
- **Date:** 2026-11-17
- **Decision owner:** Backend team
- **Scope:** Django authentication and authorization persistence
- **Related issue:** https://github.com/AirPart/airpart-backend/issues/86
- **Supersedes:** https://github.com/AirPart/airpart-backend/issues/86

## 1. Context

The AirPart ERP backend needs a persistence foundation for authentication and
role-based authorization (RBAC). The schema must represent users, roles,
permissions, user-role assignments, and role-permission assignments.

The required tables are `users`, `roles`, `permissions`, `user_roles`, and
`role_permissions`. The schema must enforce unique user emails and permission
codes.define primary and foreign keys, and include audit timestamps on
applicable tables.

The implementation is being developed with Django. SQLite is currently used
for local development, while PostgreSQL is planned for production. The final
database-engine decision is tracked separately in [ADR 0002](./0002-database-engine.md) and is not changed
by this record.

Multi-tenancy has not been confirmed as a product requirement.The design must
record the `tenant_id` consideration without introducing tenant columns,
tenant filtering, or tenant-isolation behavior in this implementation.

## 2. Decision Drivers

| #   | Driver                           | Weight | Why it matters                                                             |
| --- | -------------------------------- | ------ | -------------------------------------------------------------------------- |
| D1  | Correct relationship constraints | 5      | Invalid or duplicate role assignments must be prevented.                   |
| D2  | Django compatibility             | 5      | Models and migrations should follow the project's framework conventions.   |
| D3  | SQLite/PostgreSQL portability    | 4      | Local development and production must use the same migration history.      |
| D4  | Safe evolution of the user model | 5      | The schema must integrate with the project's configured Django user model. |
| D5  | Avoid premature tenancy behavior | 4      | Tenant isolation must not be implemented without a confirmed requirement.  |
| D6  | Auditable records                | 3      | Applicable entities need creation, update, and soft-delete timestamps.     |

## 3. Options Considered

### Option A — Django ORM models with explicit through models

- **Strengths:**
  - Uses Django's migration system and model conventions.
  - Explicit `UserRole` and `RolePermission` models can carry audit fields.
  - Database constraints can prevent duplicate user-role and role-permission
    pairs.
  - Django can generate migrations for SQLite and PostgreSQL.
- **Weaknesses:**
  - The existing user model and `AUTH_USER_MODEL` setting must be inspected
    before defining the user relationship.
  - Generated migrations still need testing against both configured database
    engines.
- **Official documentation:**
  - https://docs.djangoproject.com/en/5.2/topics/db/models/
  - https://docs.djangoproject.com/en/5.2/topics/migrations/
  - https://docs.djangoproject.com/en/5.2/ref/models/constraints/

### Option B — Handwritten SQL migrations

- **Strengths:**
  - Provides direct control over SQL definitions and database-specific
    features.
- **Weaknesses:**
  - Requires handling dialect differences between SQLite and PostgreSQL.
  - Bypasses some of Django's model and migration conventions.
  - Increases the risk of schema drift between ORM models and database tables.
- **Official documentation:**
  - https://docs.djangoproject.com/en/5.2/topics/migrations/

### Option C — Django's built-in Group and Permission tables only

- **Strengths:**
  - Uses authorization models already provided by Django.
  - Avoids defining some basic role and permission concepts from scratch.
- **Weaknesses:**
  - Does not directly establish the requested project-specific tables and
    naming (`roles`, `permissions`, `user_roles`, `role_permissions`).
  - Project-specific audit fields and relationship constraints may require
    additional models or customization.
- **Official documentation:**
  - https://docs.djangoproject.com/en/5.2/topics/auth/default/
  - https://docs.djangoproject.com/en/5.2/topics/auth/customizing/

## 4. Comparison

Scores use a 1–5 scale, where 5 is the strongest fit. Weighted values are
shown as `score × weight`.

| Criterion                        | Weight | A          | B          | C          |
| -------------------------------- | ------ | ---------- | ---------- | ---------- |
| Correct relationship constraints | 5      | 5 × 5 = 25 | 4 × 5 = 20 | 3 × 5 = 15 |
| Django compatibility             | 5      | 5 × 5 = 25 | 2 × 5 = 10 | 5 × 5 = 25 |
| SQLite/PostgreSQL portability    | 4      | 4 × 4 = 16 | 2 × 4 = 8  | 4 × 4 = 16 |
| Safe user-model integration      | 5      | 4 × 5 = 20 | 3 × 5 = 15 | 3 × 5 = 15 |
| Avoid premature tenancy behavior | 4      | 5 × 4 = 20 | 5 × 4 = 20 | 5 × 4 = 20 |
| Auditable records                | 3      | 5 × 3 = 15 | 4 × 3 = 12 | 2 × 3 = 6  |
| **Weighted total**               |        | **121**    | **85**     | **97**     |

## 5. Decision

Use Django ORM models and migrations with explicit `UserRole` and
`RolePermission` through models for the project-specific RBAC relationships.

The implementation that follows from this decision is:

1. Use the project's configured Django user model as the user entity; do not
   create a second user table without first reviewing `AUTH_USER_MODEL` and
   existing migrations
2. Ensure `users.email` is unique on the actual configured user model, subject
   to reviewing existing data and migration safety.
3. Create project-specific `Role` and `Permission` models.
4. Create explicit `UserRole` and `RolePermission` models with foreign keys
   and unique constraints on each relationship pair
5. Include `created_at`, `updated_at`, and nullable `deleted_at` fields on
   applicable project-owned tables.
6. Make permission codes unique.
7. Use Django migrations as the schema change mechanism. Validate generated
   migrations on local SQLite; validate PostgreSQL compatibility in the
   configured production-like test environment before release.
8. Do not add `tenant_id` or tenant-isolation behavior in this change.
   Revisit tenancy when a product requirement defines tenant ownership and
   isolation rules.
9. Keep development seed data in a development-only seed mechanism. Create a
   `SUPER_ADMIN` role and baseline permissions; do not create a production
   account or commit a default password.

## 6. Consequences

### Positive

- The relationships are represented explicitly and can carry audit metadata.
- Database constraints prevent duplicate role assignments and duplicate
  role-permission assignments.
- Django's migration history remains the source of truth for schema changes.
- The design does not prematurely couple authorization to an unconfirmed
  tenant model.

### Negative / Risks

- Changing the user model after initial Django migrations can be difficult and
  may require a carefully planned data migration.
- SQLite and PostgreSQL differ in some database behavior; success on SQLite
  alone does not prove production compatibility.
- Soft deletion does not automatically prevent application code from using
  deleted records; query and authorization behavior must be designed separately.
- A unique email constraint may require cleanup if existing data contains
  duplicate or null email values.

### Mitigations

- Inspect `AUTH_USER_MODEL`, existing user models, and migration history before
  implementation.
- Review generated migrations with `sqlmigrate` and run tests on each supported
  database backend.
- Add tests for relationship uniqueness, foreign keys, email uniqueness, and
  permission-code uniqueness.
- Document soft-delete semantics and ensure application queries explicitly
  account for `deleted_at`.
- Check existing email data before applying a uniqueness migration.

## 7. Rejected Options

| Option                                       | Reason for rejection                                                                                                             |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Handwritten SQL migrations                   | Rejected for this project-specific schema because they increase backend-dialect handling and risk divergence from Django models. |
| Django built-in Group/Permission tables only | Rejected as the sole schema because the task requires project-specific table names and audited relationship tables.              |

## 8. Proof of Concept / Validation

- **Branch:** `86-tech-database-design-users-roles-permissions-schema-migrations`
- **Scope of the PoC:** Create the Django models and migrations for the required
  RBAC schema, then validate them against local SQLite.
- **Acceptance criteria:**
- The required tables and foreign keys are created.
- `users.email` and `permissions.code` have unique constraints.
- Duplicate user-role and role-permission pairs are rejected.
- Applicable tables include the required audit timestamps.
- Migrations apply and roll back successfully.
- The development seed creates the `SUPER_ADMIN` role and baseline
  permissions.
- No `tenant_id` column or tenant-isolation behavior is introduced.
- The ERD is documented at `knowledge-base/diagrams/auth-erd.md`.
- **Evidence:** Add test output, migration-check results, and CI links after
  implementation.

## 9. References

- Django model documentation: https://docs.djangoproject.com/en/5.2/topics/db/models/
- Django migration documentation: https://docs.djangoproject.com/en/5.2/topics/migrations/
- Django constraints reference: https://docs.djangoproject.com/en/5.2/ref/models/constraints/
- Django authentication documentation: https://docs.djangoproject.com/en/5.2/topics/auth/
- Related database-engine decision: [`0002-database-engine.md`](./0002-database-engine.md)

## 10. Review Trigger

Reopen this decision if any of the following occurs:

- A product requirement confirms tenant ownership or tenant-level data
  isolation.
- The project changes its configured Django user model or authentication
  strategy.
- Production PostgreSQL validation reveals that the selected model constraints
  or migration plan are not portable or operationally safe.
- The authorization model requires scoped roles or permissions beyond the
  user-role and role-permission relationships defined here.
