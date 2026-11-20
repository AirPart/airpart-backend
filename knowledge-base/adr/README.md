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
- **Template:** start every new record from [`template.md`](./_TEMPLATE.md).
- **Superseded records are never deleted.** They are marked
  `Superseded by ADR-NNNN` and kept in place for history.
- **One decision per record.** If a document needs two decisions, it becomes two ADRs.
- **Link, don't copy.** Issues and pull requests link to the ADR file; they do not duplicate its content.

### Naming convention

- `NNNN` — four digits, zero-padded, assigned in order. **A number is never
  reused**, even if the record is rejected or superseded.
- `kebab-case-title` — lowercase ASCII, words separated by hyphens, no
  punctuation, ideally 3–6 words.
- Extension is always `.md`.

Examples:

0000-example.md

0001-auth-rbac-stack.md

0002-database-strategy.md

Files beginning with `_` are not records. `_TEMPLATE.md` is the template.

## ADR index

Status is one of **Proposed**, **Accepted**, **Rejected**, or
**Superseded by ADR-NNNN**.

| ID   | Title                                       | Status   | Date       | File                                                                                                   |
| ---- | ------------------------------------------- | -------- | ---------- | ------------------------------------------------------------------------------------------------------ |
| 0000 | Record architecture decisions               | Accepted | 2026-11-16 | [`0000-example.md`](./0000-example.md)                                                                 |
| 0001 | Auth and RBAC stack                         | Accepted | 2026-11-15 | [`0001-auth-rbac-stack.md`](./0001-auth-rbac-stack.md)                                                 |
| 0002 | Database Engine                             | Proposed | 2026-11-15 | [`0002-database-engine.md`](./0002-database-engine.md)                                                 |
| 0003 | Define Auth and RBAC Persistance Schema     | Proposed | 2026-11-17 | [`0003-auth-persistence-schema.md`](./0003-auth-persistence-schema.md)                                 |
| 0004 | Adopt Monorepo Layout with Shared API Types | Proposed | 2026-11-18 | [`0004-monorepo-and-shared-types-architecture.md`](./0004-monorepo-and-shared-types-architecture.md)   |
| 0005 | Frontend Serving And Container Topology     | Proposed | 2026-11-20 | [`0005-frontend-serving-and-container-topology.md`](./0005-frontend-serving-and-container-topology.md) |

> Update this table in the same commit that adds or changes a record. An index
> that lags behind is worse than no index.

## How to add an ADR

1. Copy the template: `cp knowledge-base/adr/_TEMPLATE.md knowledge-base/adr/NNNN-your-title.md`
2. Take the next free number from the index above. Never reuse one.
3. Fill in every section. If a section does not apply, write why — do not delete it.
4. Add a row to the ADR index in this file.
5. Commit both files together, before the code that implements the decision.

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

## Rules

- **One decision per record.** Two decisions in one file means neither can be
  superseded independently.
- **Write it before the code.** An ADR written afterwards is a rationalisation.
- **Link, do not copy.** Reference the code, the issue, or another ADR by path;
  duplicated content drifts.
- **Never delete a record.** Mark it `Superseded by ADR-NNNN` and leave it.
- **Anything that took more than a day to figure out belongs here**, even if it
  is not a decision.

## Templates

- ADR: [`adr/_TEMPLATE.md`](./_TEMPLATE.md)

## References

- Michael Nygard, _Documenting Architecture Decisions_: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- ADR organization and examples: https://adr.github.io
- Django 5.2 LTS release schedule: https://www.djangoproject.com/download/

```

```
