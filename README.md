# Holytail

For developers who use implementation minimizers with coding agents, the hard
failure is silent loss: the result gets shorter, but a behavior already agreed
for the task disappears. Ponytail makes the agent write less. Holytail checks
that it did not drop something you already agreed to.

Before implementation, Holytail makes the accepted behavior reviewable. After
implementation, it produces evidence that reads the result back against that
same meaning. Holytail performs no minimization and does not replace, configure,
or disable a minimizer. Activation follows the configured scope: a parent may
remain unminimized while implementation subagents use Ponytail.

## Install in Codex

Add this repository as a marketplace, then install the plugin:

```sh
codex plugin marketplace add veyndrasystems/holytail --json
codex plugin add holytail@holytail --json
```

The owner/repository syntax is supported by current Codex CLI help. This
repository has exercised a local marketplace lifecycle, not the public remote
source above, so remote installation is not claimed as verified here.

Open `/hooks`, review and trust the Holytail hook, then start a new session. A
successful hook prints:

```text
HOLYTAIL:ROUTING · evidence=hook_observed
```

That line means only that the hook ran and presented routing context. It does
not prove activation, runtime enforcement, semantic compliance, or preservation.

## Choose the authority before first use

Clear low-risk work uses `INLINE`, with a brief meaning check and proportionate
evidence in the ordinary response. Already-authorized reversible operations
are not formal merely because they have an external effect. `FULL` quality
alone does not select a route or require files, delegation, or a reviewer.

For `FORMAL` work, choose one path before copying a prompt:

- **Standalone project:** the operator or authorized lead writes
  `.holytail/accepted.md` before implementation. The lead alone writes
  `.holytail/check.md` after rereading it against the implementation snapshot.
  The worker writes only its uniquely scoped delivery.
- **Existing Soulmate project:** use its current assignment, boundary, evidence,
  and acceptance workflow. Soulmate remains authority, evidence owner, and final
  acceptor; do not initialize it or create parallel `.holytail` run state.

For a standalone formal use, replace the example with behavior you actually
accept for your task:

```text
Use $holytail:holytail with the FORMAL route. Quality mode: FULL.
Preserve accepted meaning around any enabled implementation minimizer.
This is a standalone project; do not initialize Soulmate.

Operator-authored accepted behavior: When configuration validation fails,
report every invalid key and retain the original error context.

Before editing, freeze that behavior in .holytail/accepted.md with its owner,
invariants, boundary, and unknowns. After editing, reread the same artifact and
have the lead write .holytail/check.md against the implementation snapshot,
with a finding and evidence for each invariant. The worker supplies its bounded
delivery only. Do not invent acceptance.
```

The recognizable before/after pair is:

| Evidence file | What it records |
| --- | --- |
| `.holytail/accepted.md` | Operator- or authorized-lead-owned behavior frozen before edits |
| `.holytail/check.md` | Diffable, invariant-level read-back bound to the accepted artifact and implementation snapshot |

Keep both files until the operator deliberately archives or deletes them. A
banner or bare pass is not a semantic check.

## Read the evidence correctly

Holytail keeps evidence strengths separate:

1. `hook_observed`: the session hook executed and presented context.
2. `agent_declared`: an agent asserted its own status or result.
3. Post-check evidence: `.holytail/check.md` binds findings to the accepted
   artifact and implementation snapshot.
4. Independent review: a distinct reviewer evaluates the frozen contract and
   exact artifact; this is still role-scoped evidence.
5. Final acceptance: only the operator, authorized lead, or configured
   Soulmate authority records it.

Neither a hook nor an agent assertion is independent verification. Portable
instructions are not runtime enforcement, and hook order is not authority.

## Keep the axes separate

Honor the configured minimizer scope. Ponytail `lite`, `full`, `ultra`, and
`off` control the minimizer. Holytail `FULL`/`ECO` describe quality and cost, while
`INLINE`/`FORMAL` describe the route. `full` is not `FULL`; `ultra` is not a
Holytail signal. A Holytail axis or escalation is never assigned by a Ponytail setting.
Only an explicit authorized project policy may define a mapping. Without an
exact quality assignment, report `MODE-UNBOUND`; a host `reasoningEffort` label
supplies quality only when that policy explicitly maps it.

For the complete mode, route, authority, evidence, and host-enforcement model,
read [Understand concepts and evidence](docs/concepts-and-evidence.md).

## Update, recover, or remove

Refresh the marketplace, reinstall, and confirm the result:

```sh
codex plugin marketplace upgrade holytail --json
codex plugin remove holytail@holytail --json
codex plugin add holytail@holytail --json
codex plugin list --json
```

If the add step fails, the plugin remains absent. Keep the marketplace, inspect
available plugins with
`codex plugin list --marketplace holytail --available --json`, then retry the
add. If the banner is missing, confirm installation, open `/hooks`, review and
trust the hook, and start a new session.

To remove Holytail:

```sh
codex plugin remove holytail@holytail --json
codex plugin marketplace remove holytail --json
codex plugin list --json
```

Removal does not delete `.holytail/accepted.md`, `.holytail/check.md`, or
generated host projections. Archive or delete evidence deliberately, and remove
the marketplace only when no other plugin uses it. Immutable rollback requires
an actually published known-good ref; this README does not invent one.

See [Install, verify, update, and remove](docs/operations.md) for reinstall
recovery, optional dotagents deployment, benchmark use, validation, and the
maintainer release procedure.

Holytail currently publishes no measured preservation result. Repository
validation does not establish a tagged release or immutable rollback ref. See
[CHANGELOG.md](CHANGELOG.md) for repository history and [LICENSE](LICENSE) for
licensing.
