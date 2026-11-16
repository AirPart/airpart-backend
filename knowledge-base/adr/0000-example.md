# ADR 0000 — Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-11-16
- **Decision owner:** Maintainer
- **Scope:** Engineering process, all modules
- **Related issue:** #84
- **Supersedes:** —

---

## 1. Context

This is a single-maintainer ERP. Decisions are made in conversation, in
isolation, and then implemented weeks later. The reasoning behind a choice —
which options were rejected and why — is the first thing lost, and it is
exactly what is needed when the choice is questioned six months later or when
a new contributor arrives.

The repository already holds the code. Keeping the reasoning next to the code
means the two are reviewed together, versioned together, and cannot drift
apart.

This record also serves as the worked example for
[`_TEMPLATE.md`](_TEMPLATE.md): it is short, it has one decision, and it shows
what "good enough" looks like.

## 2. Decision Drivers

| # | Driver | Weight | Why it matters |
| --- | --- | --- | --- |
| D1 | Recoverability of reasoning | 40% | The *why* is lost faster than the *what* |
| D2 | Cost of writing | 30% | A process too heavy to follow is not a process |
| D3 | Discoverability | 20% | An unreadable record is a dead record |
| D4 | Reviewability | 10% | Decisions should be reviewable before code exists |

## 3. Options Considered

### Option A — Architecture Decision Records in the repository

One Markdown file per decision, under `knowledge-base/adr/`, numbered, with a
fixed structure.

- **Strengths:** versioned with the code, reviewed in the same PR, no extra tooling, plain text.
- **Weaknesses:** no query layer; search is `grep`.
- **Official documentation:** <https://adr.github.io/>

### Option B — A wiki or Notion workspace

- **Strengths:** easy to write, good search, friendly editor.
- **Weaknesses:** lives outside the repository, so it drifts; no link between a decision and the commit that implemented it; export is lossy.
- **Official documentation:** —

### Option C — No formal record; rely on commit messages and issues

- **Strengths:** zero process cost.
- **Weaknesses:** commit messages record what changed, not what was rejected. Issue threads are chronological, not structured, and close.
- **Official documentation:** —

## 4. Comparison

| Criterion | Weight | A | B | C |
| --- | --- | --- | --- | --- |
| Recoverability of reasoning | 40% | 5 | 3 | 2 |
| Cost of writing | 30% | 4 | 5 | 5 |
| Discoverability | 20% | 3 | 5 | 2 |
| Reviewability | 10% | 5 | 2 | 1 |
| **Weighted total** | | **4.30** | **3.80** | **2.90** |

## 5. Decision

Architecture decisions are recorded as ADRs in `knowledge-base/adr/`, one file
per decision, named `NNNN-kebab-case-title.md`, written before the code that
implements them.

1. The record is written when the decision is made, not reconstructed later.
2. The record is committed in the same PR as the change it justifies.
3. A superseded record is never deleted; it is marked `Superseded by ADR-NNNN`.

## 6. Consequences

### Positive

- Every non-obvious choice has a written justification with a date.
- Rejected options stay visible, which prevents re-litigating settled questions.
- The index in [`../README.md`](../README.md) makes the whole set scannable.

### Negative / Risks

- Writing an ADR takes 30–60 minutes.
- Records can go stale if the code moves and the ADR does not.

### Mitigations

- Section 10 of every ADR names concrete review triggers.
- The index carries a status per record, so staleness is visible.

## 7. Rejected Options

| Option | Reason for rejection |
| --- | --- |
| Wiki / Notion | Fails D1 and D4: it drifts from the code and cannot be reviewed in a PR |
| Commit messages and issues only | Fails D1: records the change, not the reasoning, and issues close |

## 8. Proof of Concept / Validation

- **Branch:** —
- **Scope of the PoC:** This record, plus ADR 0001 as the first real use.
- **Acceptance criteria:** A reader can reconstruct why Django was chosen without asking anyone.
- **Evidence:** [`0001-auth-rbac-stack.md`](0001-auth-rbac-stack.md)

## 9. References

- Michael Nygard, *Documenting Architecture Decisions* — <https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions>
- ADR organisation — <https://adr.github.io/>
- MADR template — <https://adr.github.io/madr/>

## 10. Review Trigger

- More than one person joins the project and needs a different review flow.
- The number of records exceeds roughly 50 and `grep` stops being enough.
