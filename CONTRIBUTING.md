# Contributing

## Before you write code

If the change involves a non-obvious choice — a library, a schema, a
third-party service, a data model — write an ADR first.

1. Copy [`knowledge-base/adr/_TEMPLATE.md`](knowledge-base/adr/_TEMPLATE.md)
   to `knowledge-base/adr/NNNN-kebab-case-title.md`, using the next free number
   from the index.
2. Commit the record **before** the implementation, in its own commit.
3. Add the row to the [ADR index](knowledge-base/README.md#adr-index).

Naming, statuses and the full set of rules are documented in
[`knowledge-base/README.md`](knowledge-base/README.md).

## Commit messages

Conventional Commits, with the issue referenced in the footer:

```bash
<type>(<scope>): <imperative summary>

<body: why, not what>

Refs: #NN
`Closes: #NN` only when the change genuinely completes the issue.
```

## Branches

`<issue-number><type>/<kebab-case-topic>`, for example `85-docs/knowledge-base-structure` or
`85-feat/invoice-approval`.

## Definition of done

- [ ] Tests pass locally.
- [ ] No secrets, `.env` files, virtualenvs or database files are committed.
- [ ] A decision that was not obvious has an ADR.
- [ ] The knowledge base index is updated.
