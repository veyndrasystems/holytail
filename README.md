# Holytail

Holytail is a meaning-preserving implementation gate for Codex, dotagents,
and optional Soulmate workflows. It freezes accepted product meaning before
minimizing implementation mechanism. Clear work stays inline; material semantic
risk escalates to a bounded worker and, when useful, a fresh read-only reviewer.

This repository contains three distinct planes:

| Plane | Authored source | Purpose |
|---|---|---|
| Codex plugin | `plugins/holytail/` | Discover the skill and present routing at session start |
| dotagents distribution | `agents.toml` and `agents/` | Project the plugin and subagents into supported hosts |
| Soulmate control | the consumer project's `soulmate.json` and `soulmate/` | Own authority, workflow, memory rights, and run evidence |

Generated `.agents/`, `.codex/`, and `.claude/` files are disposable
projections. Do not edit or commit them as authored Holytail state.

## Why the banner was missing

The original package had a routing fragment but no installable Codex plugin or
`SessionStart` hook. dotagents subagent projection cannot create a Codex session
banner by itself. After the plugin is installed, its trusted hook displays:

```text
HOLYTAIL:ROUTING · evidence=hook_observed
```

That line proves only that Codex ran the routing hook. It does not claim that a
task has entered Holytail or that semantic compliance was verified. Every
user-visible response while Holytail is active declares both independent axes,
for example:

```text
Holytail :FULL · INLINE · evidence=agent_declared
Holytail :FULL · FORMAL · evidence=agent_declared
```

`FULL`/`ECO` are the existing team execution-quality modes. `INLINE`/`FORMAL`
are Holytail routes. Holytail never redefines one axis as the other. If no
quality mode was assigned, it reports `MODE-UNBOUND` instead of inventing one.
An exact assignment such as `Quality mode: FULL` is sufficient. Codex
`reasoningEffort=ultra` alone is not `FULL`; deriving `FULL` from it requires an
explicit mapping in the project's authorized policy.

## Install with dotagents

`agents.toml` is a consumer deployment declaration, not a manifest that is
transitively imported merely because the plugin was installed. Merge its
`[[plugins]]` and `[[subagents]]` entries into the target project's existing
manifest; do not overwrite existing agents or trust rules. If the project has a
restrictive `[trust]` table, the SSH source used here must be allowed as a git
domain path. Append this value without replacing existing entries:

```toml
[trust]
git_domains = ["github.com/veyndrasystems/holytail"]
```

The equivalent project-scoped command is:

```sh
npx --yes @sentry/dotagents@3.0.1 --project trust add github.com/veyndrasystems/holytail
```

For project scope:

```sh
npx --yes @sentry/dotagents@3.0.1 --project install
npx --yes @sentry/dotagents@3.0.1 --project sync
npx --yes @sentry/dotagents@3.0.1 --project doctor --fix
npx --yes @sentry/dotagents@3.0.1 --project doctor
```

`doctor --fix` is an explicit consumer-repository repair step. Review its diff;
among other supported repairs it merges the generated-state ignore entries such
as `agents.lock` and `.agents/.gitignore` that a fresh Soulmate project may not
yet ignore. Private-repository authentication must already be available to git;
change the source URL in the consumer manifest if that environment uses HTTPS
credentials instead of SSH.

dotagents stages the plugin bundle, marketplaces, and subagent projections; it
does not enable the native Codex plugin. From the target project root, install
the generated local marketplace entry:

```sh
codex plugin marketplace add . --json
codex plugin list --marketplace dotagents-local --available --json
codex plugin add holytail@dotagents-local --json
codex plugin list --json
```

These commands intentionally describe project scope, which is the recommended
scope for a Soulmate project. For user-global dotagents deployment, omit
`--project` from the dotagents commands and add the generated marketplace from
the dotagents base root: `codex plugin marketplace add "$HOME" --json` for the
default layout, or `codex plugin marketplace add "$DOTAGENTS_HOME" --json` when
that variable selects a custom base root. Do not run `marketplace add .` from an
arbitrary working directory.

The dotagents 3.0.1 install may warn that the authored Codex manifest is not
managed by dotagents. That warning is expected: the native manifest is retained
deliberately for Codex UI metadata and lifecycle-hook behavior; `doctor` must
still report the runtime artifacts intact.

In Codex, open `/hooks`, review and trust the bundled hook, then start a new
session. An existing conversation does not rerun `SessionStart`. The explicit
plugin skill form is `$holytail:holytail`; implicit activation is limited to
implementation work matching the skill description.

Expected project projections include:

- `.agents/plugins/holytail/skills/holytail/`
- `.agents/plugins/holytail/profiles/holytail.md` and
  `.agents/plugins/holytail/profiles/semanticreviewer.md`
- `.agents/agents/holytail.md` and `.agents/agents/semanticreviewer.md`
- `.codex/agents/holytail.toml` and `.codex/agents/semanticreviewer.toml`
- `.claude/agents/holytail.md` and `.claude/agents/semanticreviewer.md`

The Codex reviewer projection is runtime-enforced with
`sandbox_mode = "read-only"`. Other hosts receive the same reviewer instructions,
but their read-only enforcement depends on that host or on Soulmate boundaries.

## Ponytail coexistence

Holytail includes its own economy ladder, so a generic always-on Ponytail plugin
is not required. A Ponytail `:FULL` or `:ECO` banner may supply the team quality
label, but it must not bypass the Holytail gate or choose the Holytail route.
Multiple session hooks run independently; hook order is not authority. If the
installed Ponytail instructions require direct minimization before Holytail, turn
off that generic activation for the project or session and start a new session.
Holytail never changes third-party Ponytail state automatically.

## Soulmate integration

Soulmate remains the project-specific authority and evidence layer. Holytail
does not initialize Soulmate, invent a second persisted run format, grant itself
memory rights, or record final acceptance. Use
[the integration guide](plugins/holytail/skills/holytail/references/soulmate-dotagents.md) to
import the clean plugin profiles into `soulmate/agents/`, grant only
project-specific rights, and add worker-only or worker-plus-reviewer workflows.

## Validate

```sh
python3 scripts/validate.py
bash scripts/smoke-dotagents.sh
```

The first command validates package structure, manifests, references, status
contracts, and hook output without third-party Python dependencies. The smoke
test installs a copied bundle into a temporary dotagents consumer, verifies
Codex/Claude projections and the Codex reviewer sandbox, adds the generated
marketplace to an isolated Codex 0.152.1 home, and installs Holytail. Set
`HOLYTAIL_CODEX_SMOKE=0` only when intentionally skipping the native Codex
stage. Interactive hook trust and observing the next real session banner remain
operator actions.
