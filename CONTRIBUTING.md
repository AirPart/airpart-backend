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

## Code style

We follow strict Clean Code principles to ensure maximum readability, maintainbility, and modularity across the codebase:

- **File length:** Sourece code files must not exceed **400 lines**. As a rule of thumb, strive to keep files between **100 and 200 lines**, depending on the class, module, or responsibility boundaries. Smaller files are easier to reason about, test, and refactor.
- **Line Width:** The maximum width of any line of code or documentation must not exceed **120 characters**. Configure your editor or formatter (e.g., Prettier, Black, EditorConfig) accordingly to wrap or break lines cleanly.

## Branches

`<issue-number><type>/<kebab-case-topic>`, for example `85-docs/knowledge-base-structure` or
`85-feat/invoice-approval`.

## Commit messages

Conventional Commits, with the issue referenced in the footer:

```bash
<type>(<scope>): <imperative summary>

<body: why, not what>

Refs: #NN
`Closes: #NN` only when the change genuinely completes the issue.
```

## Definition of done

- [ ] Tests pass locally.
- [ ] No secrets, `.env` files, virtualenvs or database files are committed.
- [ ] A decision that was not obvious has an ADR.
- [ ] Code adheres to style limits (max 400 lines per file, 120 chars per line).
- [ ] The knowledge base index is updated.
