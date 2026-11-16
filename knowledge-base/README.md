# Knowledge Base

Institutional knowledge for the AirPart ERP backend: decisions, runbooks and
domain notes that must survive beyond individual conversations.

| Directory                         | Contents                                                            |                                  |
| --------------------------------- | ------------------------------------------------------------------- | -------------------------------- |
| [`adr/`](./adr/README.md)         | Architecture Decision Records — why the system is built this way    |                                  |
| [`research/`](research/README.md) | Investigation notes, benchmarks, vendor comparisons, spike findings | `YYYY-MM-DD-kebab-case-topic.md` |
| [`diagrams/`](diagrams/README.md) | Architecture and data-model diagrams, as editable source            | `kebab-case-name.ext`            |

## Rules

- Decisions go to `adr/`, procedures go to `runbooks/`, business rules go to `domain/`.
- No duplication: one source of truth per topic, other places link to it.
- Anything that took more than a day to figure out belongs here.

Contributor-facing workflow: [`../CONTRIBUTING.md`](../CONTRIBUTING.md).
