# Architecture Decision Records (ADR)

This directory holds the architectural decisions for the AirPart ERP backend.
Each decision is recorded **before** the related code is written, so the reasoning
behind the system stays reviewable and traceable.

## What is an ADR?

An ADR is a short, immutable document that captures one significant decision:
the context, the options considered, the choice made, and its consequences.
Decisions are never rewritten — if a decision changes, a new ADR supersedes the old one.

## Conventions

- **Numbering:** four digits, sequential, never reused (`0001`, `0002`, ...).
- **File name:** `<number>-<short-kebab-case-title>.md`.
- **Status values:** `Proposed` → `Accepted` → (`Rejected` | `Superseded by ADR-NNNN`).
- **Language:** English, to match commit messages and issue references.
- **Template:** start every new record from [`template.md`](./template.md).
- **Superseded records are never deleted.** They are marked
  `Superseded by ADR-NNNN` and kept in place for history.
- **One decision per record.** If a document needs two decisions, it becomes two ADRs.
- **Link, don't copy.** Issues and pull requests link to the ADR file; they do not duplicate its content.

## Index

| ADR                               | Title                         | Status   | Date       | Issue                                                       |
| --------------------------------- | ----------------------------- | -------- | ---------- | ----------------------------------------------------------- |
| [0001](./0001-auth-rbac-stack.md) | Authentication and RBAC stack | Accepted | 2026-11-15 | [#84](https://github.com/AirPart/airpart-backend/issues/84) |

## How to add a new ADR

1. Copy the template:

   ```bash
   cp knowledge-base/adr/template.md knowledge-base/adr/0002-<slug>.md
   ```

2. Fill in context, drivers, options, weighted comparison, decision, and consequences.
3. Set the status to `Proposed` and open a pull request.
4. On merge, change the status to `Accepted` and add a row to the index above.
5. Reference the ADR from the related issue.

## Planned decisions

The following are expected but not yet written. Numbers are assigned when the record is created.

| Topic                          | Why it matters                                                                  |
| ------------------------------ | ------------------------------------------------------------------------------- |
| Database strategy              | PostgreSQL version, migrations policy, backup/restore, naming conventions       |
| Modular monolith boundaries    | Django app layout per domain (HR, finance, sales) and inter-app contracts       |
| Multi-tenancy / branch scoping | Whether branch/department isolation lives in the data model or the policy layer |
| Background jobs                | Celery + Redis for reports, scheduled payroll, notifications                    |
| Financial reporting strategy   | Ledger model, period closing, Jalali reporting periods                          |
| File storage                   | Invoices attachments, part images, storage backend and retention                |
| Audit log and retention        | What is logged, for how long, and who can read it                               |
| Jalali calendar and timezone   | Storage in UTC, display in Jalali, period boundaries                            |
| Two-factor authentication      | Enforcement policy for privileged roles                                         |
| Deployment                     | Docker Compose layout, reverse proxy, TLS, secrets management                   |
| Backup and disaster recovery   | RPO/RTO targets and restore drills                                              |

## References

- Michael Nygard, _Documenting Architecture Decisions_: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- ADR organization and examples: https://adr.github.io
- Django 5.2 LTS release schedule: https://www.djangoproject.com/download/

```

```
