# Install, verify, update, and remove Holytail

This guide collects lifecycle, optional deployment, benchmark, validation, and
release procedures. The Codex repository marketplace is the primary install
path; dotagents is an optional projection path.

## Install and observe in Codex

```sh
codex plugin marketplace add veyndrasystems/holytail --json
codex plugin add holytail@holytail --json
codex plugin list --json
```

Codex CLI help supports an `owner/repo` Git marketplace source and the
`PLUGIN@MARKETPLACE` selector. The repository's isolated smoke exercises a local
checkout, not this public remote source, so a successful public remote install
is still unexercised.

Open `/hooks`, inspect and trust the Holytail `SessionStart` hook, and start a
new session. The expected banner is:

```text
HOLYTAIL:ROUTING · evidence=hook_observed
```

The banner means the hook ran. It is not evidence of activation, enforcement,
semantic compliance, or preservation.

## Update and reinstall recovery

Refresh the configured Git marketplace before reinstalling:

```sh
codex plugin marketplace upgrade holytail --json
codex plugin remove holytail@holytail --json
codex plugin add holytail@holytail --json
codex plugin list --json
```

If removal succeeds but the add fails, the plugin remains absent; the commands
do not roll back automatically. Keep the marketplace and inspect both its
configuration and available plugin state:

```sh
codex plugin marketplace list --json
codex plugin list --marketplace holytail --available --json
codex plugin add holytail@holytail --json
codex plugin list --json
```

If `holytail` is not available, verify that the marketplace is still listed and
retry its upgrade before adding the plugin. If the plugin is installed but the
banner is absent, open `/hooks`, review and trust the hook, and replace the
existing session with a new one. A banner observed by the operator is still
`hook_observed`, not semantic verification.

Immutable rollback requires an actually published, known-good repository ref.
No such ref is invented by this documentation, and the remote lifecycle remains
unverified until separately exercised.

## Remove and handle remnants

Remove the plugin first. Remove the marketplace only if no other installed or
available plugin relies on it, then inspect the result:

```sh
codex plugin remove holytail@holytail --json
codex plugin marketplace remove holytail --json
codex plugin list --json
```

Codex removal does not delete standalone evidence such as
`.holytail/accepted.md` and `.holytail/check.md`, or generated `.agents/`,
`.codex/`, and `.claude/` projections. Evidence may be needed for audit or
rollback context; archive or delete it only through an operator decision.

## Optional dotagents deployment

Use this only when the consumer project already chooses dotagents. Merge this
repository's `[[plugins]]` and `[[subagents]]` declarations into its existing
`agents.toml`; do not replace unrelated entries or trust rules. Add project
trust, then run the project-scoped lifecycle:

```sh
npx --yes @sentry/dotagents --project trust add github.com/veyndrasystems/holytail
npx --yes @sentry/dotagents --project install
npx --yes @sentry/dotagents --project sync
npx --yes @sentry/dotagents --project doctor --fix
npx --yes @sentry/dotagents --project doctor
```

Review the generated diff. dotagents projects files under `.agents/`, `.codex/`,
and `.claude/`; those generated files are disposable and are not authority.
Declaration and sync do not enable native Codex installation, establish hook
trust, supply runtime enforcement, or grant Soulmate authority.

For removal, delete only Holytail's declarations from the consumer manifest,
then run `dotagents sync` and `dotagents doctor`. Shared ignores, locks, trust
rules, native Codex installation, and retained evidence may remain; do not claim
automatic cleanup.

## Benchmark scaffold

The benchmark is a reproducible plan, not a preservation result:

```sh
python3 scripts/benchmark.py --self-test
python3 scripts/benchmark.py
```

The self-test exercises a deterministic accepted-behavior fixture and prints
`evaluation=status=not-run` for real model evaluation. Arm A is the active
minimizer alone. Arm B uses the same minimizer bracketed by Holytail. The
primary metric is accepted behaviors silently absent from the final
implementation.

Do not publish a preservation number from the fixture. A real evaluation must
record per-task results and variance, with model, prompt, task corpus, and host
as caveats. Until those runs exist, preservation performance is unknown.

## Validate a checkout

From the repository root, maintainers can run:

```sh
python3 scripts/validate.py
python3 tests/test_validate.py
bash scripts/smoke-dotagents.sh
python3 scripts/benchmark.py --self-test
```

The validator checks package artifacts, links in its configured scope,
metadata, axis and evidence language, workflow artifacts, public path classes,
catalog shape, and local hook behavior. The focused test mutates axis,
version-pin, privacy, and routing-note inputs to confirm rejection. The
dotagents smoke uses temporary consumer and Codex-home directories to exercise
projection plus local marketplace install/list/hook/remove behavior. It does
not establish public remote installation, hook trust in an interactive session,
runtime enforcement, or semantic preservation.

Run a relative-link check that includes the README and `docs/*.md`, because the
current validator's Markdown-link scope does not include these companion docs.
Also run `git diff --check` and review the exact bounded diff.

## Prepare—but do not imply—a release

Validation does not create a commit, tag, release, or marketplace publication.
Before release, the maintainer reviews the exact diff, runs the documented
checks, updates deployment refs in `agents.toml` to the intended immutable
published commit, and exercises the remote-source install path against that
commit. The operator chooses the version and tag under repository policy and
separately authorizes publication through the normal repository tooling.

Released bytes are immutable and must not be overwritten. Until those separate
actions occur, describe the work as implemented or exercised only within the
scope of its evidence—not as published or released.
