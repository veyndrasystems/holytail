#!/usr/bin/env python3
"""Focused negative checks for Holytail guidance and authoring boundaries."""

from __future__ import annotations

from pathlib import Path
from hashlib import sha256
import re
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
validator_source = (ROOT / "scripts" / "validate.py").read_text(encoding="utf-8")
validate_namespace = {"__name__": "holytail_validate_fixture", "__file__": str(ROOT / "scripts" / "validate.py")}
exec(compile(validator_source, str(ROOT / "scripts" / "validate.py"), "exec"), validate_namespace)

class Validator:
    validate_markdown_links = staticmethod(validate_namespace["validate_markdown_links"])
    check_axis_collision = staticmethod(validate_namespace["check_axis_collision"])
    assert_no_economy_directives = staticmethod(validate_namespace["assert_no_economy_directives"])
    assert_no_third_party_version_pins = staticmethod(validate_namespace["assert_no_third_party_version_pins"])
    assert_no_machine_local_home_paths = staticmethod(validate_namespace["assert_no_machine_local_home_paths"])
    assert_no_internal_routing_notes = staticmethod(validate_namespace["assert_no_internal_routing_notes"])
    check_guidance_boundaries = staticmethod(validate_namespace["check_guidance_boundaries"])
    check_formal_packet_quality = staticmethod(validate_namespace["check_formal_packet_quality"])
    check_routing_identity_trigger = staticmethod(validate_namespace["check_routing_identity_trigger"])
    check_worker_blocking_boundary = staticmethod(validate_namespace["check_worker_blocking_boundary"])
    validate_ci_checkout_history = staticmethod(validate_namespace["validate_ci_checkout_history"])
    validate_snapshot_bindings = staticmethod(validate_namespace["validate_snapshot_bindings"])

validate = Validator()

ci_workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
validate.validate_ci_checkout_history(ci_workflow)
for mutation in (
    lambda text: text.replace("        with:\n          fetch-depth: 0\n", "", 1),
    lambda text: text.replace("          fetch-depth: 0", "          fetch-depth: 1", 1),
    lambda text: text.replace(
        "          fetch-depth: 0", "          fetch-depth: 0\n          fetch-depth: 1", 1
    ),
    lambda text: text.replace(
        "          fetch-depth: 0", "          fetch-depth: 0\n          fetch-depth: 0", 1
    ),
):
    try:
        validate.validate_ci_checkout_history(mutation(ci_workflow))
    except AssertionError:
        pass
    else:
        raise AssertionError("CI checkout-history mutation was not rejected")

accepted_snapshot = (ROOT / ".holytail/accepted.md").read_text(encoding="utf-8")
check_snapshot = (ROOT / ".holytail/check.md").read_text(encoding="utf-8")
declared_diff = re.search(
    r"^- Implementation diff SHA-256:\s*`?([0-9a-f]{64})`?$", check_snapshot, re.MULTILINE
).group(1)
valid_check_snapshot = check_snapshot.replace(
    re.search(r"^- Contract SHA-256:\s*`?[0-9a-f]{64}`?$", check_snapshot, re.MULTILINE).group(0),
    f"- Contract SHA-256: {sha256(accepted_snapshot.encode('utf-8')).hexdigest()}",
)


def reachable_evidence(text: str) -> str:
    rows = []
    for line in text.splitlines(keepends=True):
        if re.match(r"^\|\s*I\d+\s*\|", line):
            parts = line.rstrip("\n").split("|")
            parts[3] = " `scripts/validate.py` "
            line = "|".join(parts) + ("\n" if line.endswith("\n") else "")
        rows.append(line)
    return "".join(rows)


valid_check_snapshot = reachable_evidence(valid_check_snapshot)
validate.validate_snapshot_bindings(
    accepted_snapshot,
    valid_check_snapshot,
    declared_diff,
    base_revision_exists=True,
    repo_root=ROOT,
)

invariant_row = next(line for line in valid_check_snapshot.splitlines(keepends=True) if line.startswith("| I1 |"))

for mutation in (
    lambda text: text.replace(
        re.search(r"^- Contract SHA-256:\s*`?[0-9a-f]{64}`?$", text, re.MULTILINE).group(0),
        "- Contract SHA-256: " + "0" * 64,
    ),
    lambda text: text.replace(
        re.search(r"^- Implementation diff SHA-256:\s*`?[0-9a-f]{64}`?$", text, re.MULTILINE).group(0),
        "- Implementation diff SHA-256: " + "0" * 64,
    ),
    lambda text: text.replace(
        invariant_row,
        "",
    ),
    lambda text: text.replace(
        invariant_row,
        invariant_row * 2,
    ),
    lambda text: text.replace(
        "- Contract SHA-256: " + sha256(accepted_snapshot.encode("utf-8")).hexdigest(),
        "- Contract SHA-256: malformed",
    ),
    lambda text: text.replace("`scripts/validate.py`", "missing.md", 1),
    lambda text: text.replace("`scripts/validate.py`", "`/tmp/evidence.md`", 1),
):
    try:
        validate.validate_snapshot_bindings(
            accepted_snapshot,
            mutation(valid_check_snapshot),
            declared_diff,
            base_revision_exists=True,
            repo_root=ROOT,
        )
    except AssertionError as error:
        assert "stale" in str(error)
    else:
        raise AssertionError("workflow snapshot mutation was not rejected")

with TemporaryDirectory() as directory:
    fixture_root = Path(directory)
    (fixture_root / "agents").mkdir()
    (fixture_root / "plugins" / "holytail").mkdir(parents=True)
    (fixture_root / "README.md").write_text("# fixture\n", encoding="utf-8")
    (fixture_root / "agents" / "holytail.md").write_text("# fixture\n", encoding="utf-8")
    (fixture_root / "docs" / "nested").mkdir(parents=True)
    (fixture_root / "docs" / "target.md").write_text("# section\n", encoding="utf-8")
    (fixture_root / "docs" / "guide.md").write_text(
        "[valid](target.md#section)\n[missing](missing.md#section)\n"
        "[same](#section)\n"
        "[web](https://example.test/docs)\n",
        encoding="utf-8",
    )
    (fixture_root / "docs" / "nested" / "guide.md").write_text(
        "[missing](nested-missing.md)\n",
        encoding="utf-8",
    )
    previous_root = validate_namespace["ROOT"]
    previous_plugin = validate_namespace["PLUGIN"]
    validate_namespace["ROOT"] = fixture_root
    validate_namespace["PLUGIN"] = fixture_root / "plugins" / "holytail"
    try:
        try:
            validate.validate_markdown_links()
        except AssertionError as error:
            message = str(error)
            for target in (
                "docs/guide.md -> missing.md#section",
                "docs/nested/guide.md -> nested-missing.md",
            ):
                if target not in message:
                    raise AssertionError(f"docs link failure omitted: {target}")
            if "docs/guide.md -> target.md#section" in message:
                raise AssertionError("valid relative target fragment was rejected")
        else:
            raise AssertionError("docs Markdown link mutation was not rejected")
    finally:
        validate_namespace["ROOT"] = previous_root
        validate_namespace["PLUGIN"] = previous_plugin

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
validate.check_guidance_boundaries(valid, "routing fixture", inline=True, writer=True)
validate.check_routing_identity_trigger(valid, "routing fixture")
identity_trigger = "material lifecycle/evidence/identity distinctions"
try:
    validate.check_routing_identity_trigger(
        valid.replace(identity_trigger, "material lifecycle/evidence distinctions"),
        "routing identity mutation",
    )
except AssertionError:
    pass
else:
    raise AssertionError("routing identity trigger deletion was not rejected")

validate.check_formal_packet_quality(
    "Quality mode: FULL.\nImplement the frozen accepted increment only.",
    "accepted packet",
)
for invalid_packet in (
    "Implement the frozen accepted increment only.",
    "Quality mode: FULL.\nQuality mode: FULL.",
    "Quality mode: FULL.\nQuality mode: ECO.",
    "Quality mode: FULL.\n- Quality mode: ECO.",
    "Quality mode: FULL.\nQuality  mode: ECO.",
    "Quality mode: FULL.\nQuality\tmode: ECO.",
    "Holytail :FULL · FORMAL · evidence=agent_declared",
    "Ponytail full",
    "reasoningEffort=ultra",
    "Quality mode: MODE-UNBOUND.",
):
    try:
        validate.check_formal_packet_quality(invalid_packet, "invalid packet")
    except AssertionError:
        pass
    else:
        raise AssertionError(f"formal packet mutation was not rejected: {invalid_packet}")

worker_guidance = (ROOT / "agents/holytail.md").read_text(encoding="utf-8")
validate.check_worker_blocking_boundary(worker_guidance, "worker fixture")
for old_wording, replacement in (
    ("accepted or explicitly protected options", "accepted or future options"),
    ("falls outside assignment authority", "falls within assignment authority"),
    (
        "Reversible mechanism choices that do not close an accepted or explicitly\nprotected option remain within worker authority",
        "Reversible mechanism choices remain within worker authority",
    ),
):
    regressed_worker = worker_guidance.replace(old_wording, replacement)
    try:
        validate.check_worker_blocking_boundary(regressed_worker, "regressed worker fixture")
    except AssertionError:
        pass
    else:
        raise AssertionError(f"worker blocking mutation was not rejected: {old_wording}")

for regression in (
    "Ponytail remains active and is bracketed by this workflow.",
    "Keep Ponytail active and unchanged.",
    "The user's active minimizer remains active.",
    "Before the user's already-active minimizer runs.",
    "Escalate for deletion, publication, external side effect, or other irreversible action.",
    "Escalate for deletion or external/irreversible effects.",
    "An external effect alone requires FORMAL.",
    "Escalate for all external effects.",
    "Use FORMAL for external side effects.",
    "FULL quality alone requires FORMAL.",
    "The worker writes `.holytail/check.md` after implementation.",
    "The worker also updates `.holytail/check.md`.",
    "The standalone fallback reads `.holytail/accepted.md` before the user's active minimizer and writes `.holytail/check.md` afterward.",
):
    try:
        validate.check_guidance_boundaries(valid + "\n" + regression, "regressed guidance")
    except AssertionError:
        pass
    else:
        raise AssertionError(f"guidance regression was not rejected: {regression}")

for phrase in (
    "Already-authorized reversible operations are not formal merely because they have an external effect",
    "`FULL` quality alone does not select a route",
    "lead alone writes `.holytail/check.md`",
    "worker writes only its uniquely scoped delivery",
):
    mutated = " ".join(valid.split()).replace(phrase, "")
    try:
        validate.check_guidance_boundaries(mutated, "missing boundary", inline=True, writer=True)
    except AssertionError:
        pass
    else:
        raise AssertionError(f"missing guidance boundary was not rejected: {phrase}")

for control in (
    "An external effect does not alone require FORMAL.",
    "The parent remains unminimized; implementation subagents can use Ponytail.",
    "A minimizer runs only where enabled by the configured scope.",
    "FULL quality alone does not force a formal route.",
    "The worker does not write `.holytail/check.md`.",
    "Use FORMAL for new authority, destructive effects, or persisted schema changes.",
):
    validate.check_guidance_boundaries(valid + "\n" + control, "guidance control", inline=True, writer=True)

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
