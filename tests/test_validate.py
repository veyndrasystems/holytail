#!/usr/bin/env python3
"""Focused negative check for the Ponytail/Holytail axis boundary."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
validator_source = (ROOT / "scripts" / "validate.py").read_text(encoding="utf-8")
validate_namespace = {"__name__": "holytail_validate_fixture", "__file__": str(ROOT / "scripts" / "validate.py")}
exec(compile(validator_source, str(ROOT / "scripts" / "validate.py"), "exec"), validate_namespace)

class Validator:
    check_axis_collision = staticmethod(validate_namespace["check_axis_collision"])
    assert_no_economy_directives = staticmethod(validate_namespace["assert_no_economy_directives"])
    assert_no_third_party_version_pins = staticmethod(validate_namespace["assert_no_third_party_version_pins"])
    assert_no_machine_local_home_paths = staticmethod(validate_namespace["assert_no_machine_local_home_paths"])
    assert_no_internal_routing_notes = staticmethod(validate_namespace["assert_no_internal_routing_notes"])

validate = Validator()

for path_fixture in (
    "/" + "home/" + "account/artifact",
    "/" + "Users/" + "account/artifact",
    "/" + "root/" + "account/artifact",
    "/var/" + "root/" + "artifact",
    "C:" + "\\" + "Users" + "\\" + "account" + "\\" + "artifact",
):
    try:
        validate.assert_no_machine_local_home_paths(path_fixture, "mutated path fixture")
    except AssertionError:
        pass
    else:
        raise AssertionError("machine-local path mutation was not rejected")

validate.assert_no_machine_local_home_paths("public artifact without a local path", "negative control")

for routing_fixture in (
    "Delegated to a model worker for execution.",
    "Delegation logistics belong outside this public artifact.",
    "Assignment details belong outside this public artifact.",
    "Assigned to an operator for execution.",
):
    try:
        validate.assert_no_internal_routing_notes(routing_fixture, "mutated routing fixture")
    except AssertionError:
        pass
    else:
        raise AssertionError("internal routing-note mutation was not rejected")
validate.assert_no_internal_routing_notes("Public workflow evidence remains product-facing.", "negative control")

valid = (ROOT / "plugins/holytail/skills/holytail/references/routing-context.md").read_text()
validate.check_axis_collision(valid, "fixture")

validate.assert_no_economy_directives(valid, "fixture")
economy_mutated = valid + "\n## Minimal implementation\n"
try:
    validate.assert_no_economy_directives(economy_mutated, "mutated economy fixture")
except AssertionError:
    pass
else:
    raise AssertionError("economy directive mutation was not rejected")

validate.assert_no_third_party_version_pins(valid, "fixture")
neutral_version = "9.9" + ".9"
pin_fixtures = (
    "@sentry/dotagents" + "@" + "9" + ".9.9",
    "@sentry/dotagents" + "@" + "9" + ".9",
    "@sentry/dotagents@v" + neutral_version,
    "@sentry/dotagents@^" + neutral_version,
    "@openai/codex" + "@" + "9" + ".9.9",
    "@openai/codex" + "@" + "9" + ".9",
    "@openai/codex@v" + neutral_version,
    "@openai/codex@^" + neutral_version,
    "dotagents v" + neutral_version,
    "dotagents version " + neutral_version,
    "Codex v" + neutral_version,
    "Codex version " + neutral_version,
    "Soulmate " + neutral_version,
    "Soulmate release " + neutral_version,
)
for pin_fixture in pin_fixtures:
    try:
        validate.assert_no_third_party_version_pins(valid + "\n" + pin_fixture, "mutated pin fixture")
    except AssertionError:
        pass
    else:
        raise AssertionError(f"third-party version mutation was not rejected: {pin_fixture}")

validate.assert_no_third_party_version_pins("unversioned dotagents and Codex references")
validate.assert_no_third_party_version_pins("Codex >= " + neutral_version)

for contradiction in (
    "`full` assigns `FULL`.",
    "`ultra` triggers `FORMAL`.",
    "`full` never maps to `ECO` but assigns `FULL`.",
    "`ultra` does not assign `FULL` but routes to `FORMAL`.",
    "`full` is unrelated to `ECO` and sets `FULL`.",
    "`full` does not merely suggest but assigns `FULL`.",
    "`ultra` is not advisory but routes to `FORMAL`.",
):
    axis_mutated = valid + "\n" + contradiction + "\n"
    try:
        validate.check_axis_collision(axis_mutated, "mutated axis fixture")
    except AssertionError:
        pass
    else:
        raise AssertionError(f"axis mutation was not rejected: {contradiction}")

for contradiction in ("ultra routes to FORMAL", "ultra escalates to FORMAL"):
    try:
        validate.check_axis_collision(valid + "\n" + contradiction + "\n", "route bypass fixture")
    except AssertionError:
        pass
    else:
        raise AssertionError(f"ultra route mutation was not rejected: {contradiction}")

for verb in ("assigns", "maps to", "means", "sets", "selects", "supplies", "supply", "triggers", "implies", "imply", "becomes", "is"):
    contradiction = f"`full` {verb} `FULL`."
    try:
        validate.check_axis_collision(valid + "\n" + contradiction + "\n", "mutated axis fixture")
    except AssertionError:
        pass
    else:
        raise AssertionError(f"axis mutation was not rejected: {contradiction}")

validate.check_axis_collision(valid + "\n`full` is not `FULL`.\n", "negative control")
validate.check_axis_collision(valid + "\nultra does not route to FORMAL.\n", "negative control")
validate.check_axis_collision(valid + "\nfull cannot assign FULL.\n", "negative control")
validate.check_axis_collision(valid + "\nfull never maps to FULL.\n", "negative control")
validate.check_axis_collision(valid + "\nfull is unrelated to FULL.\n", "negative control")
validate.check_axis_collision(valid + "\nultra escalates to FORMAL only under an explicit authorized project policy.\n", "policy control")
validate.check_axis_collision(valid + "\nOnly an explicit authorized project policy may define a mapping.\n", "policy control")

for contradiction in (
    "ultra routes to FORMAL without an explicit authorized project policy.",
    "full maps to FULL when no explicit authorized project policy exists.",
    "ultra routes to FORMAL unless an explicit authorized project policy applies.",
):
    try:
        validate.check_axis_collision(valid + "\n" + contradiction + "\n", "negative policy fixture")
    except AssertionError:
        pass
    else:
        raise AssertionError(f"negative policy mutation was not rejected: {contradiction}")

for routing_fixture in (
    "Requests are routed to the service.",
    "Public product traffic is routed to a supported endpoint.",
):
    validate.assert_no_internal_routing_notes(routing_fixture, "product-routing negative control")

try:
    validate.assert_no_internal_routing_notes(
        "Requests are routed to the model for execution.", "passive routing fixture"
    )
except AssertionError:
    pass
else:
    raise AssertionError("passive routing mutation was not rejected")

try:
    validate.assert_no_internal_routing_notes(
        "Requests are routed to a worker for execution.", "passive routing fixture"
    )
except AssertionError:
    pass
else:
    raise AssertionError("passive routing mutation was not rejected")

for contradiction in (
    "`full`\nassigns `FULL`.",
    "`full` directly assigns `FULL`.",
    "`full` assigns the Holytail quality mode FULL.",
    "`full` assigns `FULL`; no explicit authorized project policy exists.",
    "`full` assigns `FULL`. Only an explicit authorized project policy may define a mapping.",
    "`full` maps directly to `FULL`.",
    "`full` assigns the team quality mode `FULL`.",
):
    try:
        validate.check_axis_collision(valid + "\n" + contradiction + "\n", "structural bypass fixture")
    except AssertionError:
        pass
    else:
        raise AssertionError(f"structural axis mutation was not rejected: {contradiction}")

mutated = valid.replace("`full` is not `FULL`", "`full` assigns `FULL`")
try:
    validate.check_axis_collision(mutated, "mutated fixture")
except AssertionError:
    pass
else:
    raise AssertionError("axis mutation was not rejected")

print("validator mutation test: OK")
