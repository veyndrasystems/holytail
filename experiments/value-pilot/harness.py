#!/usr/bin/env python3
"""Deterministic planner, preparer, evaluator, and calibration self-test."""

from __future__ import annotations

import argparse
from copy import deepcopy
import difflib
from hashlib import sha256
import json
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile

import oracles


HERE = Path(__file__).resolve().parent
SOURCE_ROOT = HERE.parents[1]
MANIFEST_PATH = HERE / "manifest.json"
SCHEMA_PATH = HERE / "result.schema.json"
NOT_RUN_PREREQUISITE = (
    "fresh isolated sessions where Arms A and B inherit no Holytail or Soulmate "
    "instructions and all arms share the same observable model, reasoning, "
    "Ponytail, repository, and tool configuration, with the Holytail source "
    "checkout and its oracle/reference artifacts unavailable"
)
RESULT_KEYS = {
    "schema_version", "run_id", "task_id", "arm_id", "manifest_sha256",
    "task_sha256", "prompt_sha256", "visible_check_sha256", "starter_sha256",
    "status", "visible", "oracle", "semantic_remainder", "implementation",
    "environment", "cost", "reviewer", "correct_blockers",
    "unnecessary_blockers", "silent_loss", "evidence_limitations",
}
CONTROL_FILES = {
    "PROMPT.md", "TASK.json", "run.json", "result.template.json",
    "result.json", "visible_test.py",
}


class Invalid(ValueError):
    pass


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: bytes) -> str:
    return sha256(value).hexdigest()


def exact_keys(value: object, keys: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise Invalid(f"{label} keys mismatch")
    return value


def strings(value: object, label: str, *, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    if not isinstance(value, str) or not value:
        raise Invalid(f"{label} must be a non-empty string" if not nullable else f"{label} must be a string or null")


def string_list(value: object, label: str, *, unique: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise Invalid(f"{label} must be a string array")
    if unique and len(value) != len(set(value)):
        raise Invalid(f"{label} must contain unique values")
    return value


def nonnegative_or_null(value: object, label: str) -> None:
    if value is not None and (type(value) is not int or value < 0):
        raise Invalid(f"{label} must be a non-negative integer or null")


def load_manifest() -> dict[str, object]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    exact_keys(manifest, {"schema_version", "run_count", "prompt", "arms", "tasks", "decision_gate"}, "manifest")
    if manifest["schema_version"] != "value-pilot-manifest-v1" or manifest["run_count"] != 1:
        raise Invalid("manifest identity mismatch")
    arms = manifest["arms"]
    tasks = manifest["tasks"]
    if not isinstance(arms, list) or [arm.get("id") for arm in arms if isinstance(arm, dict)] != ["A", "B", "C"]:
        raise Invalid("manifest must contain arms A, B, and C in order")
    if not isinstance(tasks, list) or len(tasks) != 3:
        raise Invalid("manifest must contain exactly three tasks")
    if [task.get("class") for task in tasks if isinstance(task, dict)] != [
        "low-risk-control", "compatibility-trap", "authority-distinction-trap"
    ]:
        raise Invalid("task classes mismatch")
    if len({task.get("id") for task in tasks if isinstance(task, dict)}) != 3:
        raise Invalid("task IDs must be unique")
    prompt = exact_keys(manifest["prompt"], {"common_preamble", "generic_caution", "holytail_protocol"}, "prompt")
    if arms[0]["addition"] != "" or arms[1]["addition"] != prompt["generic_caution"] or arms[2]["addition"] != prompt["holytail_protocol"]:
        raise Invalid("arm additions drifted from the registered prompt controls")
    if prompt["generic_caution"] != "Preserve all explicitly accepted behavior and do not silently drop requirements.":
        raise Invalid("generic caution is not exact")
    if "Quality mode: FULL" not in prompt["holytail_protocol"] or "Keep Ponytail active" not in prompt["holytail_protocol"]:
        raise Invalid("Arm C protocol boundary is incomplete")
    gate = exact_keys(
        manifest["decision_gate"],
        {
            "production_line_allowance_minimum", "production_line_allowance_fraction",
            "broader_confirmation_task", "broader_confirmation_requires_complete_costs",
            "maximum_additional_reviewer_calls_per_task", "maximum_end_to_end_cost_ratio",
            "outcomes", "public_efficacy_claim_authorized",
        },
        "decision_gate",
    )
    if (
        gate["broader_confirmation_task"] != "legacy-settings"
        or gate["broader_confirmation_requires_complete_costs"] is not True
        or gate["production_line_allowance_minimum"] != 10
        or gate["production_line_allowance_fraction"] != 0.25
        or gate["maximum_additional_reviewer_calls_per_task"] != 1
        or gate["maximum_end_to_end_cost_ratio"] != 2.0
    ):
        raise Invalid("broader-confirmation evidence gate mismatch")
    return manifest


def source(lines: list[str]) -> str:
    if not isinstance(lines, list) or any(not isinstance(line, str) for line in lines):
        raise Invalid("fixture must be an array of lines")
    return "\n".join(lines) + "\n"


def render_prompt(manifest: dict[str, object], task: dict[str, object], arm: dict[str, object]) -> str:
    facts = json.dumps(task["canonical_facts"], ensure_ascii=False, sort_keys=True, indent=2)
    base = f"{manifest['prompt']['common_preamble']}\n\n[CANONICAL TASK FACTS]\n{facts}\n[/CANONICAL TASK FACTS]"
    return base if not arm["addition"] else f"{base}\n\n{arm['addition']}"


def fixture_digest(files: dict[str, list[str]]) -> str:
    return digest(canonical_bytes({name: source(lines) for name, lines in files.items()}))


def expected_runs(manifest: dict[str, object]) -> list[dict[str, object]]:
    manifest_hash = digest(MANIFEST_PATH.read_bytes())
    runs = []
    for task in manifest["tasks"]:
        visible = source(task["fixtures"]["visible_check"])
        for arm in manifest["arms"]:
            prompt = render_prompt(manifest, task, arm)
            runs.append({
                "schema_version": "value-pilot-run-v1",
                "run_id": f"{task['id']}--{arm['id']}--r1",
                "task_id": task["id"],
                "task_class": task["class"],
                "arm_id": arm["id"],
                "manifest_sha256": manifest_hash,
                "task_sha256": digest(canonical_bytes(task["canonical_facts"])),
                "prompt_sha256": digest(prompt.encode("utf-8")),
                "visible_check_sha256": digest(visible.encode("utf-8")),
                "starter_sha256": fixture_digest(task["fixtures"]["starter"]),
                "prompt": prompt,
            })
    return runs


def plan_document(manifest: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": "value-pilot-plan-v1",
        "manifest_sha256": digest(MANIFEST_PATH.read_bytes()),
        "evaluation": {"status": "not-run", "prerequisite": NOT_RUN_PREREQUISITE},
        "runs": expected_runs(manifest),
    }


def template_result(run: dict[str, object]) -> dict[str, object]:
    unknown_cost = {"model_calls": None, "input_tokens": None, "output_tokens": None, "duration_ms": None}
    return {
        "schema_version": "value-pilot-result-v1",
        "run_id": run["run_id"],
        "task_id": run["task_id"],
        "arm_id": run["arm_id"],
        "manifest_sha256": run["manifest_sha256"],
        "task_sha256": run["task_sha256"],
        "prompt_sha256": run["prompt_sha256"],
        "visible_check_sha256": run["visible_check_sha256"],
        "starter_sha256": run["starter_sha256"],
        "status": "replace-with-completed-or-blocked",
        "visible": {"status": "not-run", "preserved_invariants": [], "lost_invariants": [], "detail": None},
        "oracle": {"status": "not-run", "preserved_invariants": [], "lost_invariants": [], "detail": None},
        "semantic_remainder": [],
        "implementation": {"changed_files": [], "changed_lines": {"added": 0, "deleted": 0}, "new_dependencies": [], "new_abstractions": []},
        "environment": {"model": None, "reasoning": None, "host": None, "tools": None, "repository": None, "ponytail": None},
        "cost": {"implementation": dict(unknown_cost), "protocol": dict(unknown_cost), "reviewer": dict(unknown_cost)},
        "reviewer": {"required": run["arm_id"] == "C" and run["task_class"] != "low-risk-control", "verdict": "not-run", "caught_invariants": [], "disagreement": None, "detail": None},
        "correct_blockers": [],
        "unnecessary_blockers": [],
        "silent_loss": {"detected": False, "invariants": []},
        "evidence_limitations": [],
    }


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def materialize_files(directory: Path, files: dict[str, list[str]]) -> None:
    for name, lines in files.items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise Invalid("unsafe fixture path")
        target = directory.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source(lines), encoding="utf-8")


def isolation_template() -> dict[str, object]:
    return {
        "schema_version": "value-pilot-isolation-v1",
        "fresh_session_per_run": False,
        "arms_a_b_inherited_holytail_or_soulmate": True,
        "same_observable_model": False,
        "same_reasoning": False,
        "same_ponytail": False,
        "same_repository": False,
        "same_tools": False,
        "source_checkout_oracle_reference_unavailable": False,
        "no_manual_intervention": False,
        "no_repair_before_evaluation": False,
        "blinded_external_oracle": False,
        "attested_by": None,
    }


def prepare(output: Path, manifest: dict[str, object]) -> None:
    output = output.resolve()
    if output == SOURCE_ROOT or SOURCE_ROOT in output.parents:
        raise Invalid("prepare output must be outside the Holytail source checkout")
    if output.exists():
        raise Invalid("prepare output already exists; refusing to overwrite")
    if not output.parent.is_dir():
        raise Invalid("prepare output parent does not exist")
    temp = Path(tempfile.mkdtemp(prefix=f".{output.name}.preparing-", dir=output.parent))
    try:
        runs = expected_runs(manifest)
        write_json(temp / ".value-pilot.json", {
            "schema_version": "value-pilot-prepared-v1",
            "manifest_sha256": digest(MANIFEST_PATH.read_bytes()),
            "run_ids": [run["run_id"] for run in runs],
            "evaluation": {"status": "not-run", "prerequisite": NOT_RUN_PREREQUISITE},
        })
        write_json(temp / "isolation.template.json", isolation_template())
        tasks = {task["id"]: task for task in manifest["tasks"]}
        for run in runs:
            task = tasks[run["task_id"]]
            directory = temp / "runs" / run["run_id"]
            directory.mkdir(parents=True)
            materialize_files(directory, task["fixtures"]["starter"])
            (directory / "visible_test.py").write_text(source(task["fixtures"]["visible_check"]), encoding="utf-8")
            (directory / "PROMPT.md").write_text(run["prompt"] + "\n", encoding="utf-8")
            write_json(directory / "TASK.json", task["canonical_facts"])
            write_json(directory / "run.json", {key: value for key, value in run.items() if key != "prompt"})
            write_json(directory / "result.template.json", template_result(run))
        assert_no_leakage(temp, manifest)
        os.replace(temp, output)
    except BaseException:
        shutil.rmtree(temp, ignore_errors=True)
        raise


def assert_no_leakage(root: Path, manifest: dict[str, object]) -> None:
    forbidden_sources: list[bytes] = []
    for task in manifest["tasks"]:
        for fixture_name in ("reference", "mutant"):
            forbidden_sources.extend(source(lines).encode("utf-8") for lines in task["fixtures"][fixture_name].values())
    oracle_hashes = set(oracles.fingerprints())
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        lowered = path.name.lower()
        if "oracle" in lowered or "reference" in lowered or "mutant" in lowered:
            raise Invalid("prepared workspace leaked a forbidden artifact name")
        data = path.read_bytes()
        if data in forbidden_sources or digest(data) in oracle_hashes:
            raise Invalid("prepared workspace leaked a reference, mutant, or oracle implementation")


def validate_check(value: object, label: str, invariant_ids: set[str]) -> None:
    check = exact_keys(value, {"status", "preserved_invariants", "lost_invariants", "detail"}, label)
    if check["status"] not in {"pass", "fail", "not-run"}:
        raise Invalid(f"{label}.status invalid")
    preserved = string_list(check["preserved_invariants"], f"{label}.preserved_invariants", unique=True)
    lost = string_list(check["lost_invariants"], f"{label}.lost_invariants", unique=True)
    if not set(preserved + lost) <= invariant_ids or set(preserved) & set(lost):
        raise Invalid(f"{label} invariant set invalid")
    strings(check["detail"], f"{label}.detail", nullable=True)
    if check["status"] == "pass" and lost or check["status"] == "not-run" and (preserved or lost):
        raise Invalid(f"{label} status contradicts invariant results")


def validate_cost(value: object, label: str) -> None:
    cost = exact_keys(value, {"model_calls", "input_tokens", "output_tokens", "duration_ms"}, label)
    for key, item in cost.items():
        nonnegative_or_null(item, f"{label}.{key}")


def compare_text_files(expected: dict[str, str], observed: dict[str, str]) -> dict[str, object]:
    changed_files: list[str] = []
    added = deleted = 0
    for name in sorted(set(expected) | set(observed)):
        before = expected.get(name, "")
        after = observed.get(name, "")
        if before == after:
            continue
        changed_files.append(name)
        for tag, first_start, first_end, second_start, second_end in difflib.SequenceMatcher(
            None, before.splitlines(), after.splitlines(), autojunk=False
        ).get_opcodes():
            if tag in {"replace", "delete"}:
                deleted += first_end - first_start
            if tag in {"replace", "insert"}:
                added += second_end - second_start
    return {"changed_files": changed_files, "changed_lines": {"added": added, "deleted": deleted}}


def fixture_patch(task: dict[str, object]) -> dict[str, object]:
    return compare_text_files(
        {name: source(lines) for name, lines in task["fixtures"]["starter"].items()},
        {name: source(lines) for name, lines in task["fixtures"]["reference"].items()},
    )


def measure_patch(starter: dict[str, list[str]], workspace: Path) -> dict[str, object]:
    observed: dict[str, str] = {}
    for path in sorted(workspace.rglob("*")):
        if path.is_symlink():
            raise Invalid("candidate workspace contains a symlink")
        if not path.is_file():
            continue
        relative = path.relative_to(workspace).as_posix()
        parts = PurePosixPath(relative).parts
        if relative in CONTROL_FILES or "__pycache__" in parts or path.suffix == ".pyc":
            continue
        try:
            observed[relative] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise Invalid(f"candidate production file is not UTF-8 text: {relative}") from error
    expected = {PurePosixPath(name).as_posix(): source(lines) for name, lines in starter.items()}
    return compare_text_files(expected, observed)


def validate_blockers(value: object, label: str, invariant_ids: set[str]) -> None:
    if not isinstance(value, list):
        raise Invalid(f"{label} must be an array")
    for index, item in enumerate(value):
        blocker = exact_keys(item, {"invariant_id", "detail", "evidence"}, f"{label}[{index}]")
        if blocker["invariant_id"] not in invariant_ids:
            raise Invalid(f"{label}[{index}] invariant mismatch")
        strings(blocker["detail"], f"{label}[{index}].detail")
        strings(blocker["evidence"], f"{label}[{index}].evidence")


def validate_result(value: object, run: dict[str, object], task: dict[str, object]) -> dict[str, object]:
    result = exact_keys(value, RESULT_KEYS, "result")
    expected = {key: run[key] for key in (
        "run_id", "task_id", "arm_id", "manifest_sha256", "task_sha256",
        "prompt_sha256", "visible_check_sha256", "starter_sha256"
    )}
    if result["schema_version"] != "value-pilot-result-v1" or any(result[key] != expected[key] for key in expected):
        raise Invalid("result run/task/arm/hash binding mismatch")
    if result["status"] not in {"completed", "blocked"}:
        raise Invalid("result status invalid")
    invariant_ids = {item["id"] for item in task["canonical_facts"]["accepted_invariants"]}
    validate_check(result["visible"], "visible", invariant_ids)
    validate_check(result["oracle"], "oracle", invariant_ids)
    if not isinstance(result["semantic_remainder"], list):
        raise Invalid("semantic_remainder must be an array")
    for index, item in enumerate(result["semantic_remainder"]):
        remainder = exact_keys(item, {"invariant_id", "status", "detail", "source"}, f"semantic_remainder[{index}]")
        if remainder["invariant_id"] not in invariant_ids or remainder["status"] not in {"preserved", "deferred", "missing"}:
            raise Invalid("semantic remainder value mismatch")
        strings(remainder["detail"], "semantic remainder detail")
        strings(remainder["source"], "semantic remainder source")
    implementation = exact_keys(result["implementation"], {"changed_files", "changed_lines", "new_dependencies", "new_abstractions"}, "implementation")
    changed_files = string_list(implementation["changed_files"], "changed_files", unique=True)
    for filename in changed_files:
        path = PurePosixPath(filename)
        if path.is_absolute() or ".." in path.parts:
            raise Invalid("changed_files contains an unsafe path")
    lines = exact_keys(implementation["changed_lines"], {"added", "deleted"}, "changed_lines")
    for key, item in lines.items():
        if type(item) is not int or item < 0:
            raise Invalid(f"changed_lines.{key} invalid")
    string_list(implementation["new_dependencies"], "new_dependencies", unique=True)
    string_list(implementation["new_abstractions"], "new_abstractions", unique=True)
    environment = exact_keys(result["environment"], {"model", "reasoning", "host", "tools", "repository", "ponytail"}, "environment")
    for key, item in environment.items():
        strings(item, f"environment.{key}", nullable=True)
    costs = exact_keys(result["cost"], {"implementation", "protocol", "reviewer"}, "cost")
    for key, item in costs.items():
        validate_cost(item, f"cost.{key}")
    reviewer = exact_keys(result["reviewer"], {"required", "verdict", "caught_invariants", "disagreement", "detail"}, "reviewer")
    required = run["arm_id"] == "C" and run["task_class"] != "low-risk-control"
    if type(reviewer["required"]) is not bool or reviewer["required"] != required:
        raise Invalid("reviewer.required mismatch")
    if reviewer["verdict"] not in {"approved", "rework", "blocked", "not-run"}:
        raise Invalid("reviewer verdict invalid")
    caught = string_list(reviewer["caught_invariants"], "reviewer.caught_invariants", unique=True)
    if not set(caught) <= invariant_ids:
        raise Invalid("reviewer caught invariant mismatch")
    if caught and reviewer["verdict"] not in {"rework", "blocked"}:
        raise Invalid("reviewer catch requires a rework or blocked verdict")
    if reviewer["disagreement"] is not None and type(reviewer["disagreement"]) is not bool:
        raise Invalid("reviewer disagreement invalid")
    strings(reviewer["detail"], "reviewer.detail", nullable=True)
    if caught and reviewer["detail"] is None:
        raise Invalid("reviewer catch requires evidence detail")
    if required and reviewer["verdict"] == "not-run":
        raise Invalid("required reviewer was not run")
    validate_blockers(result["correct_blockers"], "correct_blockers", invariant_ids)
    validate_blockers(result["unnecessary_blockers"], "unnecessary_blockers", invariant_ids)
    blockers = result["correct_blockers"] + result["unnecessary_blockers"]
    if result["status"] == "blocked" and not blockers or result["status"] == "completed" and blockers:
        raise Invalid("completion status contradicts blockers")
    silent = exact_keys(result["silent_loss"], {"detected", "invariants"}, "silent_loss")
    if type(silent["detected"]) is not bool:
        raise Invalid("silent_loss.detected must be boolean")
    silent_ids = string_list(silent["invariants"], "silent_loss.invariants", unique=True)
    if not set(silent_ids) <= invariant_ids or silent["detected"] != bool(silent_ids):
        raise Invalid("silent_loss fields contradict")
    string_list(result["evidence_limitations"], "evidence_limitations")
    return result


def run_visible(workspace: Path) -> dict[str, object]:
    completed = subprocess.run(
        [
            sys.executable, "-I", "-c",
            "import runpy,sys; sys.path.insert(0,sys.argv[1]); runpy.run_path(sys.argv[2], run_name='__main__')",
            str(workspace.resolve()), str((workspace / "visible_test.py").resolve()),
        ], cwd=workspace,
        text=True, capture_output=True, timeout=10, check=False,
    )
    return {
        "status": "pass" if completed.returncode == 0 else "fail",
        "preserved_invariants": [], "lost_invariants": [],
        "detail": "visible check passed" if completed.returncode == 0 else "visible check failed",
    }


def validate_isolation(root: Path) -> dict[str, object]:
    path = root / "isolation.json"
    if not path.is_file():
        raise Invalid(f"evaluation remains not-run: missing isolation.json; prerequisite: {NOT_RUN_PREREQUISITE}")
    value = json.loads(path.read_text(encoding="utf-8"))
    template = isolation_template()
    exact_keys(value, set(template), "isolation")
    if value["schema_version"] != template["schema_version"]:
        raise Invalid("isolation schema mismatch")
    required_true = set(template) - {"schema_version", "arms_a_b_inherited_holytail_or_soulmate", "attested_by"}
    if any(value[key] is not True for key in required_true) or value["arms_a_b_inherited_holytail_or_soulmate"] is not False:
        raise Invalid(f"evaluation remains not-run: prerequisite not attested: {NOT_RUN_PREREQUISITE}")
    strings(value["attested_by"], "isolation.attested_by")
    return value


def aggregate_cost(records: list[dict[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for segment in ("implementation", "protocol", "reviewer"):
        output[segment] = {}
        for metric in ("model_calls", "input_tokens", "output_tokens", "duration_ms"):
            values = [record["cost"][segment][metric] for record in records]
            output[segment][metric] = None if any(value is None for value in values) else sum(values)
    return output


def derive_silent_loss(visible: dict[str, object], oracle: dict[str, object], reported: dict[str, object]) -> dict[str, object]:
    reported_ids = {
        item["invariant_id"] for item in reported["semantic_remainder"] if item["status"] in {"deferred", "missing"}
    } | {item["invariant_id"] for item in reported["correct_blockers"] + reported["unnecessary_blockers"]}
    if reported["reviewer"]["verdict"] in {"rework", "blocked"}:
        reported_ids.update(reported["reviewer"]["caught_invariants"])
    silent_ids = oracle["lost_invariants"] if visible["status"] == "pass" else []
    silent_ids = [item for item in silent_ids if item not in reported_ids]
    return {"detected": bool(silent_ids), "invariants": silent_ids}


def positive_arm_c_result(record: dict[str, object]) -> bool:
    if (
        record["status"] != "completed"
        or record["visible"]["status"] != "pass"
        or record["correct_blockers"]
        or record["unnecessary_blockers"]
        or record["silent_loss"]["detected"]
    ):
        return False
    reviewer = record["reviewer"]
    if record["oracle"]["status"] == "pass":
        return not reviewer["required"] or (
            reviewer["verdict"] == "approved"
            and reviewer["disagreement"] is False
            and not reviewer["caught_invariants"]
        )
    lost = set(record["oracle"]["lost_invariants"])
    return (
        record["oracle"]["status"] == "fail"
        and bool(lost)
        and reviewer["required"]
        and reviewer["verdict"] == "rework"
        and lost <= set(reviewer["caught_invariants"])
    )


def decide(records: list[dict[str, object]], manifest: dict[str, object]) -> dict[str, object]:
    by = {(record["task_id"], record["arm_id"]): record for record in records}
    if len(by) != 9:
        raise Invalid("decision requires exactly nine task/arm records")
    tasks = [task["id"] for task in manifest["tasks"]]
    trap_tasks = [task["id"] for task in manifest["tasks"] if task["class"] != "low-risk-control"]
    missed = lambda record: record["visible"]["status"] == "pass" and record["oracle"]["status"] == "fail" and record["silent_loss"]["detected"]
    positive_c = [task for task in tasks if positive_arm_c_result(by[(task, "C")])]
    unique_c = [task for task in tasks if missed(by[(task, "A")]) and missed(by[(task, "B")]) and task in positive_c]
    equivalent = all(
        (by[(task, "B")]["oracle"]["status"], by[(task, "B")]["silent_loss"]["detected"])
        == (by[(task, "C")]["oracle"]["status"], by[(task, "C")]["silent_loss"]["detected"])
        for task in tasks
    )
    common_control_holytail_misses = [task for task in trap_tasks if missed(by[(task, "B")]) and missed(by[(task, "C")])]
    lines = {
        arm: sum(record["implementation"]["changed_lines"]["added"] + record["implementation"]["changed_lines"]["deleted"] for record in records if record["arm_id"] == arm)
        for arm in ("A", "B", "C")
    }
    task_by_id = {task["id"]: task for task in manifest["tasks"]}
    line_comparisons = []
    for task_id in tasks:
        reference = fixture_patch(task_by_id[task_id])["changed_lines"]
        reference_total = reference["added"] + reference["deleted"]
        c_lines = by[(task_id, "C")]["implementation"]["changed_lines"]
        c_total = c_lines["added"] + c_lines["deleted"]
        allowance = max(
            manifest["decision_gate"]["production_line_allowance_minimum"],
            math.ceil(reference_total * manifest["decision_gate"]["production_line_allowance_fraction"]),
        )
        line_comparisons.append({
            "task_id": task_id,
            "reference_lines": reference_total,
            "arm_c_lines": c_total,
            "allowance_lines": allowance,
            "within_allowance": c_total <= reference_total + allowance,
        })
    c_new_dependencies = sum(len(record["implementation"]["new_dependencies"]) for record in records if record["arm_id"] == "C")
    c_new_abstractions = sum(len(record["implementation"]["new_abstractions"]) for record in records if record["arm_id"] == "C")
    economy_retained = all(item["within_allowance"] for item in line_comparisons) and c_new_dependencies == 0 and c_new_abstractions == 0
    missing_cost_values = sum(
        value is None
        for record in records
        for segment in record["cost"].values()
        for value in segment.values()
    )
    costs_complete = missing_cost_values == 0
    cost_comparisons = []
    costs_comparable = costs_complete
    cost_excessive = False
    if costs_complete:
        for task_id in tasks:
            b_record = by[(task_id, "B")]
            c_record = by[(task_id, "C")]
            b_tokens = sum(segment["input_tokens"] + segment["output_tokens"] for segment in b_record["cost"].values())
            c_tokens = sum(segment["input_tokens"] + segment["output_tokens"] for segment in c_record["cost"].values())
            b_duration = sum(segment["duration_ms"] for segment in b_record["cost"].values())
            c_duration = sum(segment["duration_ms"] for segment in c_record["cost"].values())
            additional_reviewer_calls = c_record["cost"]["reviewer"]["model_calls"] - b_record["cost"]["reviewer"]["model_calls"]
            meaningful = b_tokens > 0 and b_duration > 0
            within = (
                meaningful
                and c_tokens <= b_tokens * manifest["decision_gate"]["maximum_end_to_end_cost_ratio"]
                and c_duration <= b_duration * manifest["decision_gate"]["maximum_end_to_end_cost_ratio"]
                and additional_reviewer_calls <= manifest["decision_gate"]["maximum_additional_reviewer_calls_per_task"]
            )
            costs_comparable = costs_comparable and meaningful
            cost_excessive = cost_excessive or (meaningful and not within)
            cost_comparisons.append({
                "task_id": task_id,
                "arm_b_tokens": b_tokens,
                "arm_c_tokens": c_tokens,
                "arm_b_duration_ms": b_duration,
                "arm_c_duration_ms": c_duration,
                "additional_reviewer_calls": additional_reviewer_calls,
                "meaningful_denominators": meaningful,
                "within_ceiling": within,
            })
    costs_acceptable = costs_complete and costs_comparable and not cost_excessive
    c_blocked_records = [
        record["run_id"] for record in records
        if record["arm_id"] == "C" and (
            record["status"] != "completed"
            or record["correct_blockers"]
            or record["unnecessary_blockers"]
            or record["reviewer"]["verdict"] == "blocked"
        )
    ]
    friction = (
        bool(c_blocked_records)
        or not economy_retained
        or cost_excessive
    )
    compatibility_catch = manifest["decision_gate"]["broader_confirmation_task"] in unique_c
    if friction:
        outcome = "friction-limited-routing"
    elif equivalent and common_control_holytail_misses:
        outcome = "collapse-to-rule"
    elif unique_c == ["publication-authority"] and costs_acceptable:
        outcome = "soulmate-primary"
    elif compatibility_catch and costs_acceptable:
        outcome = "broader-confirmation"
    else:
        outcome = "inconclusive"
    return {
        "outcome": outcome,
        "positive_arm_c_tasks": positive_c,
        "unique_arm_c_catches": unique_c,
        "arm_c_blocked_records": c_blocked_records,
        "common_control_holytail_misses": common_control_holytail_misses,
        "production_patch_economy": {
            "changed_lines_by_arm": lines,
            "arm_c_reference_comparisons": line_comparisons,
            "arm_c_new_dependencies": c_new_dependencies,
            "arm_c_new_abstractions": c_new_abstractions,
            "retained": economy_retained,
        },
        "cost_by_arm": {arm: aggregate_cost([record for record in records if record["arm_id"] == arm]) for arm in ("A", "B", "C")},
        "cost_evidence": {
            "complete": costs_complete,
            "comparable": costs_comparable,
            "acceptable": costs_acceptable,
            "excessive": cost_excessive,
            "missing_values": missing_cost_values,
            "comparisons": cost_comparisons,
        },
        "public_efficacy_claim_authorized": False,
        "evidence_limit": "A 3x3x1 diagnostic screen cannot support a public efficacy claim.",
    }


def evaluate(root: Path, manifest: dict[str, object]) -> dict[str, object]:
    root = root.resolve()
    marker_path = root / ".value-pilot.json"
    if not marker_path.is_file():
        raise Invalid("evaluate output is not a prepared value-pilot directory")
    if (root / "evaluation.json").exists():
        raise Invalid("evaluation.json already exists; refusing to overwrite")
    isolation = validate_isolation(root)
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    runs = expected_runs(manifest)
    exact_keys(marker, {"schema_version", "manifest_sha256", "run_ids", "evaluation"}, "prepared marker")
    if marker["schema_version"] != "value-pilot-prepared-v1" or marker["manifest_sha256"] != digest(MANIFEST_PATH.read_bytes()) or marker["run_ids"] != [run["run_id"] for run in runs]:
        raise Invalid("prepared marker mismatch")
    tasks = {task["id"]: task for task in manifest["tasks"]}
    records = []
    for run in runs:
        directory = root / "runs" / run["run_id"]
        task = tasks[run["task_id"]]
        registered_metadata = {key: value for key, value in run.items() if key != "prompt"}
        if json.loads((directory / "run.json").read_text(encoding="utf-8")) != registered_metadata:
            raise Invalid(f"run metadata mismatch: {run['run_id']}")
        if (directory / "PROMPT.md").read_text(encoding="utf-8") != run["prompt"] + "\n":
            raise Invalid(f"prompt mismatch: {run['run_id']}")
        if canonical_bytes(json.loads((directory / "TASK.json").read_text(encoding="utf-8"))) != canonical_bytes(task["canonical_facts"]):
            raise Invalid(f"task facts mismatch: {run['run_id']}")
        visible_source = source(task["fixtures"]["visible_check"])
        if (directory / "visible_test.py").read_text(encoding="utf-8") != visible_source:
            raise Invalid(f"visible check mismatch: {run['run_id']}")
        result_path = directory / "result.json"
        if not result_path.is_file():
            raise Invalid(f"evaluation remains not-run: missing result.json for {run['run_id']}")
        reported = validate_result(json.loads(result_path.read_text(encoding="utf-8")), run, task)
        observed = deepcopy(reported)
        observed["implementation"].update(measure_patch(task["fixtures"]["starter"], directory))
        observed["visible"] = run_visible(directory)
        observed["oracle"] = oracles.run_oracle(run["task_id"], directory)
        observed["silent_loss"] = derive_silent_loss(observed["visible"], observed["oracle"], reported)
        records.append(observed)
    comparable = ("model", "reasoning", "host", "tools", "repository", "ponytail")
    if any(len({json.dumps(record["environment"][key], sort_keys=True) for record in records}) != 1 for key in comparable):
        raise Invalid("environment identities differ across runs")
    report = {
        "schema_version": "value-pilot-evaluation-v1",
        "status": "evaluated",
        "manifest_sha256": digest(MANIFEST_PATH.read_bytes()),
        "isolation_attestation": isolation,
        "records": records,
        "decision": decide(records, manifest),
        "evidence_limitations": [
            "Oracle outcomes were computed externally and do not trust candidate oracle self-report.",
            "Blocker and reviewer classifications are operator-recorded, not oracle-proven.",
            "Isolation is operator-attested, not independently verified by this harness.",
            "One run per cell is diagnostic and cannot estimate variance or establish product efficacy."
        ],
    }
    target = root / "evaluation.json"
    temporary = root / ".evaluation.json.tmp"
    write_json(temporary, report)
    os.replace(temporary, target)
    return report


def valid_fixture_result(run: dict[str, object]) -> dict[str, object]:
    result = template_result(run)
    result["status"] = "completed"
    if result["reviewer"]["required"]:
        result["reviewer"].update({"verdict": "approved", "caught_invariants": [], "disagreement": False, "detail": "fixture reviewer"})
    return result


def synthetic_records(manifest: dict[str, object]) -> list[dict[str, object]]:
    records = []
    for run in expected_runs(manifest):
        result = valid_fixture_result(run)
        result["visible"]["status"] = "pass"
        result["oracle"]["status"] = "pass"
        result["implementation"]["changed_lines"]["added"] = 4
        records.append(result)
    return records


def self_test() -> None:
    manifest = load_manifest()
    json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    runs = expected_runs(manifest)
    expected_ids = [f"{task['id']}--{arm}--r1" for task in manifest["tasks"] for arm in ("A", "B", "C")]
    assert [run["run_id"] for run in runs] == expected_ids and len(runs) == 9
    for task in manifest["tasks"]:
        prompts = {arm["id"]: render_prompt(manifest, task, arm) for arm in manifest["arms"]}
        marker = "[CANONICAL TASK FACTS]\n"
        end = "\n[/CANONICAL TASK FACTS]"
        facts = [prompt.split(marker, 1)[1].split(end, 1)[0] for prompt in prompts.values()]
        assert len(set(facts)) == 1
        assert prompts["B"] == prompts["A"] + "\n\n" + manifest["prompt"]["generic_caution"]
        assert prompts["C"] == prompts["A"] + "\n\n" + manifest["prompt"]["holytail_protocol"]
    try:
        prepare(SOURCE_ROOT / "value-pilot-output", manifest)
    except Invalid as error:
        assert "outside the Holytail source checkout" in str(error)
    else:
        raise AssertionError("prepare accepted an output inside the source checkout")
    with tempfile.TemporaryDirectory(prefix="holytail-value-pilot-") as temporary:
        prepared = Path(temporary) / "prepared"
        prepare(prepared, manifest)
        assert sorted(path.name for path in (prepared / "runs").iterdir()) == sorted(expected_ids)
        assert_no_leakage(prepared, manifest)
        early_exit_task = "__self_test_early_exit__"
        oracles.ORACLES[early_exit_task] = (
            ("EARLY", "raise SystemExit(0)"),
            ("NOISY", "print('unexpected candidate output')"),
        )
        try:
            early_exit_workspace = Path(temporary) / "early-exit"
            early_exit_workspace.mkdir()
            early_exit_result = oracles.run_oracle(early_exit_task, early_exit_workspace)
            assert early_exit_result == {
                "status": "fail",
                "preserved_invariants": [],
                "lost_invariants": ["EARLY", "NOISY"],
                "detail": "2 external hidden check(s) failed",
            }
        finally:
            del oracles.ORACLES[early_exit_task]
        for task in manifest["tasks"]:
            for fixture_name, expected_oracle in (("reference", "pass"), ("mutant", "fail")):
                workspace = Path(temporary) / f"{task['id']}-{fixture_name}"
                workspace.mkdir()
                materialize_files(workspace, task["fixtures"][fixture_name])
                (workspace / "visible_test.py").write_text(source(task["fixtures"]["visible_check"]), encoding="utf-8")
                assert run_visible(workspace)["status"] == "pass"
                assert oracles.run_oracle(task["id"], workspace)["status"] == expected_oracle
        task_by_id = {task["id"]: task for task in manifest["tasks"]}
        for run in runs:
            directory = prepared / "runs" / run["run_id"]
            materialize_files(directory, task_by_id[run["task_id"]]["fixtures"]["reference"])
            reported = valid_fixture_result(run)
            reported["implementation"].update({
                "changed_files": ["fabricated.py"],
                "changed_lines": {"added": 999, "deleted": 999},
            })
            write_json(directory / "result.json", reported)
        isolation = isolation_template()
        for key in isolation:
            if key not in {"schema_version", "arms_a_b_inherited_holytail_or_soulmate", "attested_by"}:
                isolation[key] = True
        isolation.update({
            "arms_a_b_inherited_holytail_or_soulmate": False,
            "attested_by": "deterministic fixture calibration",
        })
        write_json(prepared / "isolation.json", isolation)
        evaluated = evaluate(prepared, manifest)
        assert all(record["implementation"]["changed_files"] != ["fabricated.py"] for record in evaluated["records"])
        assert all(record["implementation"]["changed_lines"] != {"added": 999, "deleted": 999} for record in evaluated["records"])
        assert evaluated["decision"]["public_efficacy_claim_authorized"] is False
        measurement_workspace = Path(temporary) / "measurement"
        measurement_workspace.mkdir()
        (measurement_workspace / "sample.py").write_text("first\nchanged\n", encoding="utf-8")
        (measurement_workspace / "added.py").write_text("added\n", encoding="utf-8")
        (measurement_workspace / "result.json").write_text("ignored control\n", encoding="utf-8")
        assert measure_patch({"sample.py": ["first", "original"]}, measurement_workspace) == {
            "changed_files": ["added.py", "sample.py"],
            "changed_lines": {"added": 2, "deleted": 1},
        }
    valid = valid_fixture_result(runs[0])
    validate_result(valid, runs[0], task_by_id[runs[0]["task_id"]])
    for mutation in (
        lambda item: item.update(run_id="wrong"),
        lambda item: item.update(task_id="wrong"),
        lambda item: item.update(arm_id="C"),
        lambda item: item.update(prompt_sha256="0" * 64),
        lambda item: item.update(unexpected=True),
        lambda item: item.update(status="unknown"),
        lambda item: item["reviewer"].update(caught_invariants=["LR1"]),
    ):
        invalid = deepcopy(valid)
        mutation(invalid)
        try:
            validate_result(invalid, runs[0], task_by_id[runs[0]["task_id"]])
        except Invalid:
            pass
        else:
            raise AssertionError("invalid result record was accepted")
    def mark_losses(records: list[dict[str, object]], task_id: str, invariant_id: str, arms: set[str]) -> None:
        for record in records:
            if record["task_id"] == task_id and record["arm_id"] in arms:
                record["oracle"] = {"status": "fail", "preserved_invariants": [], "lost_invariants": [invariant_id], "detail": "fixture"}
                record["silent_loss"] = {"detected": True, "invariants": [invariant_id]}

    def zero_costs(records: list[dict[str, object]]) -> None:
        for record in records:
            for segment in record["cost"].values():
                segment.update({"model_calls": 0, "input_tokens": 0, "output_tokens": 0, "duration_ms": 0})

    def meaningful_costs(records: list[dict[str, object]]) -> None:
        zero_costs(records)
        for record in records:
            record["cost"]["implementation"].update({"model_calls": 1, "input_tokens": 50, "output_tokens": 50, "duration_ms": 100})
            if record["arm_id"] == "C":
                record["cost"]["protocol"].update({"input_tokens": 10, "duration_ms": 10})
                if record["reviewer"]["required"]:
                    record["cost"]["reviewer"].update({"model_calls": 1, "input_tokens": 10, "output_tokens": 10, "duration_ms": 10})

    all_pass = synthetic_records(manifest)
    meaningful_costs(all_pass)
    assert decide(all_pass, manifest)["outcome"] == "inconclusive"

    collapse = deepcopy(all_pass)
    mark_losses(collapse, "legacy-settings", "CP2", {"B", "C"})
    assert decide(collapse, manifest)["outcome"] == "collapse-to-rule"

    equivalent_friction = deepcopy(collapse)
    low_risk = next(record for record in equivalent_friction if record["task_id"] == "low-risk-rename" and record["arm_id"] == "C")
    low_risk["status"] = "blocked"
    low_risk["unnecessary_blockers"] = [{"invariant_id": "LR1", "detail": "fixture", "evidence": "fixture"}]
    assert decide(equivalent_friction, manifest)["outcome"] == "friction-limited-routing"

    soulmate = synthetic_records(manifest)
    mark_losses(soulmate, "publication-authority", "AU2", {"A", "B"})
    assert decide(soulmate, manifest)["outcome"] == "inconclusive"
    meaningful_costs(soulmate)
    assert decide(soulmate, manifest)["outcome"] == "soulmate-primary"

    broader = synthetic_records(manifest)
    mark_losses(broader, "legacy-settings", "CP2", {"A", "B"})
    assert decide(broader, manifest)["outcome"] == "inconclusive"
    zero_costs(broader)
    assert decide(broader, manifest)["outcome"] == "inconclusive"
    meaningful_costs(broader)
    assert decide(broader, manifest)["outcome"] == "broader-confirmation"

    blocked_catch = deepcopy(broader)
    blocked_record = next(record for record in blocked_catch if record["task_id"] == "legacy-settings" and record["arm_id"] == "C")
    blocked_record["status"] = "blocked"
    blocked_record["oracle"] = {"status": "fail", "preserved_invariants": [], "lost_invariants": ["CP2"], "detail": "fixture"}
    blocked_record["correct_blockers"] = [{"invariant_id": "CP2", "detail": "claimed blocker", "evidence": "operator record"}]
    blocked_record["silent_loss"] = {"detected": False, "invariants": []}
    assert decide(blocked_catch, manifest)["outcome"] == "friction-limited-routing"

    visible_failure = deepcopy(broader)
    visible_failure_record = next(record for record in visible_failure if record["task_id"] == "legacy-settings" and record["arm_id"] == "C")
    visible_failure_record["visible"] = {"status": "fail", "preserved_invariants": [], "lost_invariants": [], "detail": "fixture"}
    assert decide(visible_failure, manifest)["outcome"] == "inconclusive"

    blocked_review = deepcopy(broader)
    blocked_review_record = next(record for record in blocked_review if record["task_id"] == "legacy-settings" and record["arm_id"] == "C")
    blocked_review_record["oracle"] = {"status": "fail", "preserved_invariants": [], "lost_invariants": ["CP2"], "detail": "fixture"}
    blocked_review_record["silent_loss"] = {"detected": False, "invariants": []}
    blocked_review_record["reviewer"].update({"verdict": "blocked", "caught_invariants": ["CP2"], "detail": "CP2 was identified"})
    assert decide(blocked_review, manifest)["outcome"] == "friction-limited-routing"

    remainder_only = deepcopy(broader)
    remainder_record = next(record for record in remainder_only if record["task_id"] == "legacy-settings" and record["arm_id"] == "C")
    remainder_record["oracle"] = {"status": "fail", "preserved_invariants": [], "lost_invariants": ["CP2"], "detail": "fixture"}
    remainder_record["silent_loss"] = {"detected": False, "invariants": []}
    remainder_record["semantic_remainder"] = [{"invariant_id": "CP2", "status": "missing", "detail": "reported", "source": "fixture"}]
    assert decide(remainder_only, manifest)["outcome"] == "inconclusive"

    reviewed_catch = deepcopy(broader)
    reviewed_record = next(record for record in reviewed_catch if record["task_id"] == "legacy-settings" and record["arm_id"] == "C")
    reviewed_record["oracle"] = {"status": "fail", "preserved_invariants": [], "lost_invariants": ["CP2"], "detail": "fixture"}
    reviewed_record["silent_loss"] = {"detected": False, "invariants": []}
    reviewed_record["reviewer"].update({"verdict": "rework", "caught_invariants": ["CP2"], "detail": "CP2 was identified"})
    assert decide(reviewed_catch, manifest)["outcome"] == "broader-confirmation"

    tiny_b = deepcopy(broader)
    for record in tiny_b:
        if record["arm_id"] == "B":
            record["implementation"]["changed_lines"] = {"added": 0, "deleted": 0}
    assert decide(tiny_b, manifest)["outcome"] == "broader-confirmation"

    excessive_lines = deepcopy(broader)
    reference = fixture_patch(task_by_id["legacy-settings"])["changed_lines"]
    reference_total = reference["added"] + reference["deleted"]
    allowance = max(
        manifest["decision_gate"]["production_line_allowance_minimum"],
        math.ceil(reference_total * manifest["decision_gate"]["production_line_allowance_fraction"]),
    )
    next(record for record in excessive_lines if record["task_id"] == "legacy-settings" and record["arm_id"] == "C")["implementation"]["changed_lines"] = {
        "added": reference_total + allowance + 1, "deleted": 0,
    }
    assert decide(excessive_lines, manifest)["outcome"] == "friction-limited-routing"

    for field in ("new_dependencies", "new_abstractions"):
        excessive = deepcopy(broader)
        next(record for record in excessive if record["arm_id"] == "C")["implementation"][field] = ["fixture"]
        assert decide(excessive, manifest)["outcome"] == "friction-limited-routing"

    for segment, metric, value in (
        ("reviewer", "model_calls", 2),
        ("implementation", "input_tokens", 201),
        ("implementation", "duration_ms", 201),
    ):
        excessive = deepcopy(broader)
        target = next(record for record in excessive if record["task_id"] == "legacy-settings" and record["arm_id"] == "C")
        target["cost"][segment][metric] = value
        assert decide(excessive, manifest)["outcome"] == "friction-limited-routing"

    wrong_task = synthetic_records(manifest)
    mark_losses(wrong_task, "low-risk-rename", "LR2", {"A", "B"})
    meaningful_costs(wrong_task)
    assert decide(wrong_task, manifest)["outcome"] == "inconclusive"

    reviewer_report = valid_fixture_result(next(run for run in runs if run["task_id"] == "legacy-settings" and run["arm_id"] == "C"))
    reviewer_report["reviewer"].update({"verdict": "rework", "caught_invariants": [], "detail": "unrelated issue"})
    failed_oracle = {"status": "fail", "preserved_invariants": [], "lost_invariants": ["CP2"], "detail": "fixture"}
    passed_visible = {"status": "pass", "preserved_invariants": [], "lost_invariants": [], "detail": "fixture"}
    assert derive_silent_loss(passed_visible, failed_oracle, reviewer_report) == {"detected": True, "invariants": ["CP2"]}
    reviewer_report["reviewer"].update({"caught_invariants": ["CP1"], "detail": "unrelated CP1 issue"})
    assert derive_silent_loss(passed_visible, failed_oracle, reviewer_report) == {"detected": True, "invariants": ["CP2"]}
    reviewer_report["reviewer"].update({"caught_invariants": ["CP2"], "detail": "CP2 was identified"})
    assert derive_silent_loss(passed_visible, failed_oracle, reviewer_report) == {"detected": False, "invariants": []}

    print("self-test status=ok runs=9 prompts=controlled schema=fail-closed oracles=calibrated decisions=5 economy=reference-bounded costs=bounded blockers=friction reviewer-catches=invariant-specific isolation=source-separated")
    print("evaluation=status=not-run prerequisite=" + NOT_RUN_PREREQUISITE.replace(" ", "-"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("plan")
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("output", type=Path)
    evaluate_parser = subparsers.add_parser("evaluate")
    evaluate_parser.add_argument("output", type=Path)
    args = parser.parse_args()
    manifest = load_manifest()
    if args.self_test:
        self_test()
    elif args.command == "plan":
        print(json.dumps(plan_document(manifest), ensure_ascii=False, sort_keys=True, indent=2))
    elif args.command == "prepare":
        prepare(args.output, manifest)
        print(f"prepared={args.output} runs=9 evaluation=status=not-run prerequisite={NOT_RUN_PREREQUISITE.replace(' ', '-')}")
    elif args.command == "evaluate":
        report = evaluate(args.output, manifest)
        print(f"evaluation=status={report['status']} outcome={report['decision']['outcome']} public_efficacy_claim_authorized=false")
    else:
        parser.print_help()
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Invalid, json.JSONDecodeError, OSError, subprocess.SubprocessError) as error:
        print(f"value-pilot: FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
