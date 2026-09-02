# Worked example: preserve contextual identity

## Accepted meaning

A subject may be known in one context and unknown in another. Context owners
have independent authority. There is no accepted global identity or global
registry, and raw source evidence must remain reachable.

Protected distinction:

| A | B | Why distinct |
|---|---|---|
| subject known in context X | subject known in context Y | knowledge and authority are context-local |
| local reference | global identity | a global identity has not been accepted or proven |
| raw source record | derived summary | the summary cannot replace provenance |

## Rejected shortcut

A single `users(id)` table with one global identifier is smaller, but it silently
asserts cross-context equivalence, centralizes authority, and collapses
known/unknown states. That representation is outside the accepted semantic
space because it silently asserts equivalence and authority.

## Faithful representation

Represent identity with a context-qualified key such as
`(context_id, local_reference)` and retain the raw-source locator. Do not add a
global resolver until an authorized decision accepts its meaning, collision
rules, authority, and migration.

## Route

- Adding one in-memory context-qualified map behind an existing interface may be
  `INLINE` if no persisted or public contract changes.
- Introducing a persisted global identity schema is `FORMAL` because it changes
  identity, authority, persistence, and migration semantics.

The active implementation workflow may choose mechanism only after the accepted
distinctions remain observable. The difference is semantic, not code size.
