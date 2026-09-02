# Holytail

Minimizers can make an agent's implementation shorter by silently dropping a
behavior you already agreed to. Ponytail makes the agent write less. Holytail checks that it did not drop something you already agreed to.

Holytail freezes accepted meaning before your active minimizer runs, then reads
that meaning back against the implementation. It performs no minimization and
does not replace, configure, or disable your minimizer.

## How it works

1. The operator or authorized lead supplies the accepted increment.
2. Holytail brackets the active minimizer with a pre-work freeze and a
   post-work check.
3. The check reports each invariant, its evidence, and unknowns.

Without Soulmate, `.holytail/accepted.md` is the standalone, human-readable
authority artifact and `.holytail/check.md` is the diffable post-check artifact.
The check names the accepted artifact and implementation snapshot; a banner or
bare pass is not a semantic check. Keep these artifacts until deliberately
archived or deleted. When Soulmate is present, it remains optional project
authority, evidence owner, and final acceptor. Holytail does not initialize it,
grant memory rights, or create a second run format.

## Install in Codex (primary)

Add the public repository marketplace by owner/repository name, then install the
plugin:

```sh
codex plugin marketplace add veyndrasystems/holytail --json
codex plugin add holytail@holytail --json
```

Open `/hooks`, review and trust the hook, then start a new session. The hook's
`HOLYTAIL:ROUTING · evidence=hook_observed` line means only that the hook ran.
It does not prove activation, compliance, or semantic preservation.

The catalog is `.agents/plugins/marketplace.json`; it is a repo marketplace,
not universal-directory publication. It points to `./plugins/holytail` and is
the only authored file under the otherwise disposable `.agents/` projection
tree.

## First use and expected files

Copy this prompt into an implementation session:

```text
Use $holytail:holytail. Before editing, freeze the accepted behavior in
.holytail/accepted.md. Keep the user's active minimizer active. After editing,
reread that same accepted artifact and write a diffable .holytail/check.md
against the implementation snapshot. The operator or authorized lead owns the
accepted content; do not invent acceptance.
```

In a standalone project, the expected evidence files are:

| File | Role |
|---|---|
| `.holytail/accepted.md` | Operator/authorized-lead-owned accepted behavior before edits |
| `.holytail/check.md` | Diffable read-back against the implementation snapshot |

See the [semantic-contract reference](plugins/holytail/skills/holytail/references/semantic-contract.md)
for the full formal fields. In a Soulmate project, use its existing assignment,
boundary, evidence, and acceptance workflow; do not create parallel state.

Generated host projections are disposable:

| Host | Discovery and activation | Tested behavior | Runtime enforcement | Instruction/protocol | Host/operator-owned gap |
|---|---|---|---|---|---|
| Codex | Repo marketplace, plugin add, trusted `SessionStart` hook | Validator and isolated marketplace smoke exercise install/list/hook/remove | Native `semanticreviewer` profile is read-only only when that profile is actually used | Skill, status axes, contract, and delivery protocol | Operator must review/trust hook and observe a real new-session result |
| Claude projection | dotagents optional projection | Existing dotagents smoke checks projection and hook files | Instructions do not enforce read-only behavior | Portable profiles and hook configuration | Host trust and enforcement are Claude/operator-owned |
| Soulmate (optional) | Existing configured project workflow | No Soulmate state is initialized by this package | Soulmate boundary and run controls | Soulmate owns authority, evidence, memory rights, and final acceptance | Existing Soulmate setup and decisions are operator-owned |

`agent_declared` is an assertion, not verification. Independent verification is
separate evidence. Portable hosts carry instructions only. Hook order is not
authority. Holytail never mutates third-party plugin state.

## Ponytail integration and axes

Keep Ponytail active. Ponytail `lite`, `full`, `ultra`, and `off` settings and any
Ponytail banner or intensity are unrelated to Holytail's `FULL`/`ECO` quality
and `INLINE`/`FORMAL` route. `full` is not `FULL`; `ultra` is not a Holytail
signal. Neither assigns a Holytail axis or triggers escalation. Only an
explicit authorized project policy can define a mapping. If no exact quality
assignment exists, Holytail reports `MODE-UNBOUND`; a `reasoningEffort` label
supplies quality only when that policy explicitly maps it.

## Update and uninstall

To refresh a configured repository marketplace and reinstall its plugin:

```sh
codex plugin marketplace upgrade holytail --json
codex plugin remove holytail@holytail --json
codex plugin add holytail@holytail --json
codex plugin list --json
```

If re-adding fails, the plugin remains absent. Keep the marketplace, inspect its
available state, and retry:

```sh
codex plugin marketplace list --json
codex plugin list --marketplace holytail --available --json
codex plugin add holytail@holytail --json
```

Immutable rollback requires an actually published known-good repository ref;
this documentation does not invent one.

To remove it, uninstall the plugin first. Remove the marketplace only when no
other plugin uses it, then list afterward:

```sh
codex plugin remove holytail@holytail --json
codex plugin marketplace remove holytail --json
codex plugin list --json
```

These commands do not automatically delete `.holytail/accepted.md`,
`.holytail/check.md`, or generated projections. Remove or archive evidence only
deliberately. Optional dotagents removal reverses only Holytail declarations in
the consumer manifest, then runs `dotagents sync` and `dotagents doctor`; shared
ignores, locks, trust, and native installation may remain.

## Optional dotagents deployment

Merge this repository's `[[plugins]]` and `[[subagents]]` declarations into the
consumer `agents.toml` without replacing existing entries. Add project trust
first without replacing existing trust rules, then run the actual project-scoped
commands:

```sh
npx --yes @sentry/dotagents --project trust add github.com/veyndrasystems/holytail
npx --yes @sentry/dotagents --project install
npx --yes @sentry/dotagents --project sync
npx --yes @sentry/dotagents --project doctor --fix
npx --yes @sentry/dotagents --project doctor
```

Review the generated diff. dotagents projects Claude/Codex files under
`.agents/`, `.codex/`, and `.claude/`; those projections are disposable. Its
declaration and sync do not enable native Codex installation or grant Soulmate
authority. Remove only Holytail declarations when uninstalling, then sync and
doctor; do not claim automatic cleanup.

## Benchmark scaffold (no result claimed)

`python3 scripts/benchmark.py --self-test` runs a deterministic fixture and
prints `status=not-run` for real model evaluation. `python3 scripts/benchmark.py`
prints the same single-command evaluation plan. Arm A runs the minimizer alone;
arm B runs the same minimizer bracketed by Holytail. Each task declares accepted
behaviors, and the primary metric is the count of accepted behaviors silently
dropped by the final implementation. Record per-task results and variance only
after real runs; model, prompt, task-corpus, and host differences are caveats.
This repository publishes no preservation number.

## Validate and release

```sh
python3 scripts/validate.py
python3 tests/test_validate.py
bash scripts/smoke-dotagents.sh
python3 scripts/benchmark.py --self-test
```

The validator checks required artifacts, links, metadata, axes, evidence
limits, workflow language, and catalog shape. The focused test mutates the axis
contract and proves the validator rejects economy, pin, and axis regressions. The dotagents smoke
uses a temporary consumer and preserves generated projection checks; its native
stage uses a temporary Codex home and installs, lists, exercises the current
hook, removes the plugin, removes the marketplace, and lists again. Hook trust
and semantic preservation in a real session remain unexercised unless observed.

Before a public release, review the exact diff, run the validation commands,
and confirm the documented checks do not create commits, tags, releases, or
publish. The operator chooses the version and tag, updates the changelog, and
separately authorizes publication through the normal repository tooling.

See [CHANGELOG.md](CHANGELOG.md) for release history and
[LICENSE](LICENSE) for licensing. Troubleshooting details, including why the
banner may be absent, are kept in the changelog and the hook/install sections.
