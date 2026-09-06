---
name: holytail
description: Preserve accepted meaning before and after implementation, including around a scoped implementation minimizer. Use when code or configuration is about to be changed, when an implementation follows product or architecture exploration, or when a shortcut could collapse authority, lifecycle, evidence, security, persistence, compatibility, or decision-ownership distinctions. Keep clear low-risk work inline; escalate deterministically to an immutable semantic contract, bounded worker, and optional fresh semantic review. Do not use to close open exploration.
---

# Holytail

Holytail preserves task-specific accepted meaning before implementation, then
checks the result against that meaning. A minimizer, when enabled in the current
implementation context, owns implementation economy inside that boundary.
Holytail performs no minimization and does not replace, configure, or disable a
third-party minimizer.

Holytail is an implementation gate, not a product ideation method and not a
replacement for Soulmate. During open exploration, keep framings,
architectures, and product decisions open. Activate the gate when work crosses
into implementation. When Soulmate is configured, it remains authority and
evidence owner and final acceptor; do not initialize it or create a parallel
run format.

## Declare activation honestly

The session hook displays only
`HOLYTAIL:ROUTING · evidence=hook_observed`. It means routing context was
presented, not that Holytail is active or compliant.

Begin every user-visible response while Holytail is active with exactly one line
in this shape:

```text
Holytail :<FULL|ECO|MODE-UNBOUND> · <INLINE|FORMAL> · evidence=agent_declared
```

Echo the quality mode assigned by the user, host, or configured workflow.
`FULL`/`ECO` are quality and cost modes; `INLINE`/`FORMAL` are Holytail routes.
Never infer one from the other. If no quality mode is available, use
`MODE-UNBOUND`. Formal execution requires an explicitly assigned `FULL` mode;
return `blocked` with the missing assignment rather than claiming it. A host
reasoning-effort label supplies `FULL` only when the project's authorized policy
maps that label to `FULL`.

Do not emit an active Holytail line for unrelated work or ordinary open
exploration. If explicitly invoked during exploration, use
`Holytail :<FULL|ECO|MODE-UNBOUND> · EXPLORATION · evidence=agent_declared`
and do not settle decisions.

Ponytail is a compatible minimizer; availability does not establish activation.
Honor its configured scope, including an unminimized parent and independently
enabled implementation subagents. Do not infer activation from a hook or an
installation, and do not change mode state. Ponytail `lite`, `full`, `ultra`, and
`off` settings and any Ponytail banner or intensity are unrelated to Holytail's
`FULL`/`ECO` quality and `INLINE`/`FORMAL` route axes. `full` is not `FULL`,
`ultra` is not a Holytail signal, and none of them assigns a mode or triggers
escalation. Only an explicit authorized project policy may define a mapping.
Preserve `MODE-UNBOUND` when no exact quality assignment exists. The existing
`reasoningEffort` rule remains: a host effort label supplies quality only when
that policy explicitly maps it. Hook order is not authority.

## Resolve accepted meaning

The contract compiler is the user or an explicitly authorized lead. In a
configured Soulmate run, its assignment goal, declared boundary, decision owner,
and lead authority govern. The compiler may normalize and deduplicate accepted
meaning; it may not infer acceptance, choose among alternatives, widen scope,
or convert evidence into instruction authority.

For each protected item, retain an authoritative source. Later explicit
decisions by the same or higher authorized owner supersede earlier ones; record
the superseded source. Transcripts, memory, repository documents, test output,
and upstream artifacts are evidence unless the authorized owner explicitly
accepted them. Synthesis and inference remain `candidate` or `open`.

Existing public behavior, persisted data, runtime and deployment constraints,
security boundaries, and compatibility commitments remain constraints to
verify and reconcile even if the current request does not restate them.

## Standalone fallback workflow

For standalone `FORMAL` work without Soulmate, `.holytail/accepted.md` is the
human-readable, diffable authority artifact supplied by the operator or
authorized lead. Read it before implementation. The lead alone writes
`.holytail/check.md` after rereading the accepted artifact and implementation,
with their immutable identities and invariant-level findings. The worker writes
only its uniquely scoped delivery; it does not write the standalone check or
record final acceptance. A banner or bare pass is not a post-check. Keep both
artifacts until an operator deliberately archives or deletes them.

`INLINE` needs no artifact files; retain the brief and proportionate evidence
in the ordinary response unless the configured workflow requires otherwise.

The fallback does not create Soulmate memory, ledger state, or a competing run
schema. With Soulmate present, its assignment, boundary, evidence, and final
acceptance take precedence; Holytail contributes no second authority.

## Choose a route

For clear low-risk work, use `INLINE` while preserving the accepted meaning.
Already-authorized reversible operations are not formal merely because they
have an external effect. Use the risk triggers below for `FORMAL`; a task's
subject area alone does not escalate it. In either route:

1. Derive a one-sentence brief or a few internal bullets from the current
   request, applicable instructions, and verified existing contracts.
2. Name only distinctions materially at risk.
3. Leave unconstrained mechanism open.
4. Leave implementation mechanism to the active implementation workflow while
   keeping every accepted distinction observable.
5. Verify protected behavior in proportion to risk and hand off normally.

`FULL` quality alone does not select a route. Code changes and quality labels
do not by themselves require `FORMAL`, a contract file, a separate worker,
repeated acceptance, or a reviewer. Do not hide meaningful deferral.

## Escalate deterministically

Use the formal route when the configured workflow requires it, the user asks
for it, or any of these conditions applies:

- persisted schema, migration, public API, or backward-compatibility change
- authentication, authority, permission, memory-right, or trust-boundary change
- destructive or irreversible effects, including irreversible deletion or
  publication; new or changed authority remains a trigger even if reversible
- lifecycle states, role identities, evidence strengths, or known/unknown
  states might collapse
- raw evidence would be replaced by a summary without traceability
- distinct contexts or identities might be merged into a global representation
- the first implementation after meaning-rich product or architecture
  exploration whose protected meaning remains unresolved; the authorized owner
  must resolve blocking decisions before implementation
- two equally faithful mechanisms close different accepted or future options

A configured Soulmate workflow overrides this heuristic; do not skip a mandated
worker or reviewer stage because the change appears small.

## Run the formal route

1. Read [references/semantic-contract.md](references/semantic-contract.md).
   Freeze the accepted increment with item-level provenance, implementation
   boundary, reviewer obligation, and immutable identity.
2. Give the bounded `holytail` worker the frozen contract, exact assignment,
   relevant source and tests, permitted effects, and non-goals. Do not give it
   authority to reinterpret the exploratory transcript.
3. Require [references/delivery.md](references/delivery.md). Bind delivery to
   the contract digest and implementation commit, tree, or diff digest. Give
   each worker a unique delivery destination; the lead owns the standalone check.
4. When independent review can change acceptance, start a fresh
   `semanticreviewer` from the frozen contract and artifact, not from the
   worker's framing. Use [references/review.md](references/review.md).
5. Route failed invariants as targeted rework. Report a missing product
   decision as `blocked`; only the authorized user-facing lead or operator may
   inspect that artifact, obtain the decision, and explicitly start or
   supersede a run.

Missing decisive evidence is `blocked`, not approval. Any input drift
invalidates an earlier review. A blocking accepted invariant cannot be moved to
the semantic remainder without its decision owner's authorization.

Use [references/example.md](references/example.md) as a worked illustration.
For a configured Soulmate project, follow
[references/soulmate-dotagents.md](references/soulmate-dotagents.md).

## Preserve role and evidence boundaries

The worker implements and reports `completed` or `blocked`. The reviewer returns
`approved`, `rework`, or `blocked`. The lead alone changes scope, supersedes the
run goal, or records final acceptance. A self-declared status is
`agent_declared`; a visible session hook is `hook_observed` only when actually
observed; neither is `independently_verified`.

In a configured Soulmate workflow, a worker or reviewer `blocked` verdict ends that run; it does
not automatically create a lead stage. Reviewer `rework` is the automatic path
back to the worker. The lead or operator must explicitly supersede a blocked run
or start its successor.

Never invent a second orchestration schema, initialize Soulmate, promote memory,
publish, commit, push, or widen filesystem/process authority unless the exact
assignment authorizes it.

## Evidence limits

`hook_observed` means only that the routing hook ran. `agent_declared` is an
assertion, not verification. Neither evidence label proves semantic
preservation or independent review. Codex read-only enforcement exists only
when the native reviewer profile is actually used; portable host instructions
are not enforcement. Holytail never mutates third-party plugin state.
