# Knowledge Base

Institutional knowledge for the AirPart ERP backend: decisions, runbooks and
domain notes that must survive beyond individual conversations.

| Directory                 | Contents                                                                |
| ------------------------- | ----------------------------------------------------------------------- |
| [`adr/`](./adr/README.md) | Architecture Decision Records — why the system is built this way        |
| `runbooks/`               | Operational procedures (deploy, restore, incident response) — _planned_ |
| `domain/`                 | Business rules for HR, finance and sales — _planned_                    |
| `api/`                    | API conventions and versioning policy — _planned_                       |

## Rules

- Decisions go to `adr/`, procedures go to `runbooks/`, business rules go to `domain/`.
- No duplication: one source of truth per topic, other places link to it.
- Anything that took more than a day to figure out belongs here.
