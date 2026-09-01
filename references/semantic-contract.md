# Semantic contract

This is the formal escalation template, not a per-task requirement. For clear
low-risk work, the user's current request and accepted project instructions are
the semantic brief; perform the Holytail gate inline and continue. Use this
template only when material meaning or a protected distinction needs explicit
agreement.

Keep this smaller than the exploratory conversation. Discard repetition,
superseded alternatives, unrelated context, and reasoning narratives.

```text
Status: candidate | accepted
Owner:
Approved by:
Related task or run:
```

## Problem

State the problem independently of a proposed mechanism.

## Accepted meaning

State what the resulting behavior means. Mark each statement `accepted`,
`candidate`, `open`, `rejected`, or `future`.

## Protected distinctions

| A | B | Why they must remain distinct |
|---|---|---|

## Invariants and negative requirements

- Invariant:
- Must not:

## Observable success

| Condition | Evidence expected |
|---|---|

## Compatibility

- Persisted formats:
- CLI and paths:
- Migration and historical evidence:

## Security and privacy boundary

- Authority and content authority:
- Filesystem and process:
- Secrets and unattended execution:

## Explicit non-goals

-

## Open decisions

| Decision | Owner | Blocking? |
|---|---|---:|

## Expected semantic remainder

List meaningful parts that may remain deferred after the first implementation.

Formal acceptance gate: the goal is no longer exploratory; accepted meaning,
protected distinctions, invariants, negative requirements, non-goals,
implementation boundary, reviewer obligation, and blocking decisions are
explicit. Existing user or authorized-lead statements count as acceptance.
Request a new acceptance only for a blocking ambiguity or meaning-changing
choice.
