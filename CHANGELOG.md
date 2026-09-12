# Changelog

## [0.1.0] - 2026-09-06

### Changed

- Repositioned Holytail as a bracket around an already-active minimizer.
- Added standalone `.holytail/accepted.md` and post-check evidence, native Codex
  repo-marketplace packaging, lifecycle guidance, and an honest benchmark
  scaffold.

### Fixed

- Keep implementation minimization scoped to implementation subagents while
  preserving Holytail's meaning and evidence boundary.
- Allow proportionate inline checks for clear low-risk work and assign the
  standalone post-check to the lead.
- Pin consumer deployment entries to the released commit.

## [Unreleased]

### Changed

- Add standing risk-based quality selection and exact formal-child packet
  preflight guidance without changing the child-side fail-closed boundary.

### Troubleshooting

The banner may be absent when the plugin is not installed, its hook is not
trusted, or an existing session has not been replaced with a new session.
`HOLYTAIL:ROUTING · evidence=hook_observed` means only that the hook ran; it is
not semantic verification. Review `/hooks`, trust the hook, and start a new
session after installation.

## Release procedure

Review the exact diff and run the documented validator, isolated install smoke,
and benchmark self-test. Before tagging, maintainers update the deployment refs
in `agents.toml` to the intended immutable published commit and exercise the
remote-source install path against that published commit. The operator chooses
the release version and tag under repository policy, then separately authorizes
the tag and release with the normal repository tooling. Do not overwrite
released bytes.
