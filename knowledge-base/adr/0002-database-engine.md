# ADR 0002 — Database Engine and Data Durability Strategy

- **Status:** Proposed
- **Date:** 2026-11-15
- **Decision owner:** Product owner / developer (solo maintainer)
- **Scope:** Persistence layer — engine choice, version policy, backup and restore
- **Related ADR:** [0001](./0001-auth-rbac-stack.md)
- **Related issue:** https://github.com/AirPart/airpart-backend/issues/86

---

## 1. Context

The ERP persists three kinds of data with different guarantees:

1. **Financial records** — invoices, invoice lines, receipts, payments, ledger entries.
   Amounts must be exact (no floating point), and reports must aggregate across
   periods, branches and accounts.
2. **HR records** — employees, contracts, attendance, payroll runs. Payroll is
   periodic, batch-oriented and must be reproducible for a closed period.
3. **Catalogue and sales** — aircraft parts, customers, orders, quotations.
   Mostly CRUD with search on part numbers and descriptions, in Persian and English.

Constraints that shape the choice:

- **Solo maintainer.** Whoever writes the code also runs the database, the backups
  and the restore drills. Operational simplicity is a feature.
- **Deployment:** Docker on a manually managed server in phase one; CI/CD later.
- **Load:** a single company, one to a few dozen concurrent users. Not high-traffic.
  Write concurrency is low; read/report concurrency is moderate.
- **Data volume is small by database standards.** Even at 50 invoices per working
  day for five years, the invoice tables stay in the low millions of rows.
- **Localisation:** Persian text, Jalali dates displayed on top of UTC storage,
  IRR amounts with no minor unit in practice.
- **Lifetime:** the system must run and be restorable for years, across Django
  and OS upgrades.
- **Growth path:** branches/departments may be added, and reporting may later want
  a read replica or a separate analytics path.

This ADR decides the engine **before** any domain model is written, so that
migrations, backup procedures and reporting queries are built against the real target.

### Scope boundary

This ADR does **not** decide the ORM abstraction, the caching layer or the
reporting tool. It decides the engine, its version policy, and how data is
backed up and restored.

---

## 2. Decision Drivers

| #   | Decision driver                                                  | Weight |
| --- | ---------------------------------------------------------------- | ------ |
| D1  | Correctness of financial arithmetic and complex reporting        | 25%    |
| D2  | Operational cost and cognitive load for a solo maintainer        | 20%    |
| D3  | Django and ecosystem support (migrations, admin, extensions)     | 20%    |
| D4  | Backup, restore and durability (RPO/RTO, point-in-time recovery) | 15%    |
| D5  | Growth path: concurrency, partitioning, replication, analytics   | 10%    |
| D6  | Licensing cost and hosting availability in Iran                  | 10%    |

D1 and D2 dominate deliberately: for an accounting-adjacent ERP, a wrong number is
worse than a slow page, and an unmaintainable database is worse than a slower one.

---

## 3. Options Considered

### Option A — PostgreSQL

- **Strengths:**
  - Exact `NUMERIC` arithmetic, and the richest aggregation toolkit for financial
    reports: window functions, CTEs, `GROUPING SETS`/`ROLLUP`, `FILTER`,
    ordered-set aggregates.
  - First-class Django support, including `django.contrib.postgres` (arrays, ranges,
    `JSONB`, `SearchVector`, `GinIndex`).
  - `JSONB` for flexible attributes (part specifications) without schema churn.
  - `pg_trgm` and ICU collations give workable Persian search and correct sorting.
  - Real durability story: WAL archiving, point-in-time recovery, `pg_basebackup`,
    logical replication for a future reporting replica.
  - Declarative partitioning for append-only tables (audit log, ledger history).
  - Permissive licence (PostgreSQL License), no vendor lock-in, widely hosted.
- **Weaknesses:**
  - More knobs than SQLite: connection limits, autovacuum, backup scheduling.
  - Major-version upgrades require a dump/restore or `pg_upgrade` rehearsal.
  - Needs a running server process, even in development.

### Option B — MySQL 8.4 LTS / MariaDB 11.4 LTS

- **Strengths:**
  - Mature, widely hosted, multi-year LTS windows, familiar to many operators.
  - Window functions and CTEs are available in current versions.
  - Solid `DECIMAL` support.
- **Weaknesses:**
  - Django's PostgreSQL-specific features are unavailable, so the reporting layer
    loses tools that are directly useful here.
  - Historical footguns around transaction isolation, implicit casts and
    `utf8mb4` collation behaviour add review burden.
  - The MySQL/MariaDB split means advice and tooling do not always transfer.
  - No advantage over PostgreSQL for this project's workload.

### Option C — SQLite

- **Strengths:**
  - Zero operations. No server, no ports, no connection pool, no tuning.
  - Backup is a file copy (`VACUUM INTO` gives a consistent snapshot).
  - Excellent for development and for the test suite — fast, isolated, disposable.
  - Supports window functions and CTEs; more capable than its reputation.
- **Weaknesses:**
  - **Single writer.** Concurrent writes serialise; long reports block writes.
  - No users, roles or network access — access control lives entirely in the app.
  - No point-in-time recovery; the durability story is "copy the file often".
  - No partitioning, no replication, no `JSONB` equivalent with indexing parity.
  - Type affinity is loose: constraints that PostgreSQL enforces can silently pass.

### Option D — Microsoft SQL Server — **screened out**

- **Reason for rejection:** licensing cost and Windows-centric operations for a
  solo maintainer on Linux/Docker. Not evaluated further.

---

## 4. Comparison

Scores range from 1 (poor) to 5 (excellent). Weighted score = Σ(weight × score).

| Criterion                                | Weight | A: PostgreSQL | B: MySQL/MariaDB | C: SQLite |
| ---------------------------------------- | ------ | ------------- | ---------------- | --------- |
| Financial correctness and reporting (D1) | 25%    | **5**         | 4                | 4         |
| Operational cost (D2)                    | 20%    | 4             | 4                | **5**     |
| Django and ecosystem support (D3)        | 20%    | **5**         | 4                | 4         |
| Backup, restore, durability (D4)         | 15%    | **5**         | 4                | 3         |
| Growth path (D5)                         | 10%    | **5**         | 4                | 1         |
| Licensing and hosting in Iran (D6)       | 10%    | **5**         | **5**            | **5**     |
| **Weighted score**                       | 100%   | **4.80**      | 4.10             | 3.85      |

### Notes on the key scores

- **D1:** PostgreSQL wins on the reporting toolkit, not on `NUMERIC` (all three are
  exact). The deciding factor is `GROUPING SETS`, `FILTER` and window functions
  combined with `JSONB` — the shape of financial and catalogue reporting here.
- **D2:** SQLite wins outright. PostgreSQL is second: one container, one backup
  job, and a very large body of operational knowledge to lean on.
- **D4:** Only PostgreSQL and MySQL offer point-in-time recovery. For payroll and
  ledger data, "restore to 14:32 yesterday" is a real requirement, not a luxury.
- **D5:** SQLite is scored 1 because there is no path from it to concurrent writers
  or a replica without changing engines. That is precisely the migration this ADR
  exists to avoid doing twice.

---

## 5. Decision

**Option A is proposed:**

> **PostgreSQL as the production database, pinned to a specific major version
> (17 at the time of writing), with SQLite retained as the development and
> test default.**

Concretely:

1. **Production:** PostgreSQL in Docker, data on a named volume or a host bind mount,
   `migrate` in the entrypoint, no `latest` tag.
2. **Development:** SQLite by default for speed; `docker compose -f docker-compose.yml
-f docker-compose.postgres.yml up` when a database-specific issue needs reproducing.
3. **CI:** the test suite runs against **both** SQLite and PostgreSQL from day one.
   A decision is not accepted on SQLite-only evidence.
4. **Version policy:** pin the major version; schedule a major upgrade rehearsal
   once per year, with a tested restore before and after.
5. **Backups:** nightly `pg_dump` plus WAL archiving for point-in-time recovery;
   a restore drill is part of the release checklist, not an afterthought.

The status stays **Proposed** until the validation plan in section 8 is executed.

---

## 6. Consequences

### Positive

- Reporting queries can use the full SQL toolkit instead of being reshaped around
  engine limits.
- Point-in-time recovery becomes possible, which is the minimum bar for payroll and
  ledger data.
- A single engine covers OLTP, reporting and later analytics, so no second store
  is introduced prematurely.
- Django's PostgreSQL-specific features remain available if the domain needs them.
- No licensing cost and no vendor lock-in.

### Negative / Risks

- **Two engines to keep honest.** SQLite in development and PostgreSQL in production
  can diverge. Mitigated by running CI against both, and by treating PostgreSQL as
  the reference when behaviour differs.
- **Operational surface grows.** Backups, restores, upgrades and monitoring are now
  the maintainer's job. Mitigated by scripting them early and rehearsing restores.
- **Major-version upgrades** need planning. Mitigated by the annual rehearsal and by
  never running `latest`.
- **SQLite's loose typing** can let a bug pass locally that PostgreSQL rejects.
  Mitigated by CI on PostgreSQL and by explicit `CheckConstraint`s in models.

### Risk mitigations

- CI matrix: SQLite + PostgreSQL on every push.
- `pg_dump` nightly, WAL archiving enabled, retention documented.
- A written restore procedure in `knowledge-base/runbooks/`, rehearsed quarterly.
- Version pinned in `docker-compose.yml`; upgrade requires an ADR amendment or a
  superseding ADR if the target major changes the plan.

---

## 7. Rejected Options

| Option                               | Reason for rejection                                                                                                                                                                                                                                             |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MySQL 8.4 LTS / MariaDB 11.4 LTS** | Viable and well supported, but it offers no advantage over PostgreSQL for this workload while giving up the PostgreSQL-specific reporting and `JSONB` features that fit the domain. The MySQL/MariaDB ecosystem split also adds ambiguity for a solo maintainer. |
| **SQLite as the production engine**  | Zero operations and genuinely sufficient for the current data volume, but a single writer, no point-in-time recovery and no replication path make it a dead end for payroll and ledger data. Retained for development and tests, rejected for production.        |
| **Microsoft SQL Server**             | Screened out: licensing cost and Windows-centric operations for a solo Linux/Docker maintainer. Not evaluated further.                                                                                                                                           |

---

## 8. Validation Plan (how this moves from Proposed to Accepted)

The decision is accepted only when all of the following hold:

- [ ] The PoC from ADR 0001 passes its test suite on **PostgreSQL** in CI.
- [ ] A representative reporting query (period totals per branch, with `GROUPING SETS`
      or window functions) runs against a seeded dataset of at least 1,000,000
      invoice-line rows within an acceptable time budget.
- [ ] A restore drill succeeds: take a `pg_dump`, drop the database, restore it,
      and verify row counts and a checksum on the ledger table.
- [ ] Point-in-time recovery is demonstrated once on a scratch database.
- [ ] The Docker Compose file and the `.env.example` reflect the final configuration.
- [ ] Backup and restore steps are written into `knowledge-base/runbooks/`.

If any item fails, the ADR is amended or a superseding ADR is written — the record
is never silently edited.

---

## 9. References

### Official documentation

- PostgreSQL: https://www.postgresql.org/docs/
- PostgreSQL versioning policy: https://www.postgresql.org/support/versioning/
- PostgreSQL backup and PITR: https://www.postgresql.org/docs/current/continuous-archiving.html
- Django database notes: https://docs.djangoproject.com/en/5.2/ref/databases/
- `django.contrib.postgres`: https://docs.djangoproject.com/en/5.2/ref/contrib/postgres/
- MySQL 8.4 LTS: https://dev.mysql.com/doc/refman/8.4/en/
- MariaDB releases: https://mariadb.org/about/#maintenance-policy
- SQLite: https://www.sqlite.org/docs.html
- SQLite `VACUUM INTO`: https://www.sqlite.org/lang_vacuum.html
- `pg_trgm`: https://www.postgresql.org/docs/current/pgtrgm.html

### Internal references

- ADR 0001 (auth and RBAC stack): `knowledge-base/adr/0001-auth-rbac-stack.md`
- ADR template: `knowledge-base/adr/template.md`

---

## 10. Review Trigger

This decision is revisited if any of the following occurs:

- Sustained write concurrency exceeds what a single PostgreSQL instance comfortably
  handles on the target server.
- Reporting volume outgrows a single instance and a read replica or columnar store
  becomes necessary.
- The hosting environment cannot provide reliable PostgreSQL backups or point-in-time
  recovery.
- A managed database service becomes the better trade-off than self-hosting.
- PostgreSQL's supported major versions no longer match the Django version in use.
