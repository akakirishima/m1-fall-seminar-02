"""Compact AI entry point and deterministic index of saved experiment records.

No model or external source is executed. Only Python's standard library is used.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATES = {"planned", "running", "completed", "failed", "interrupted"}
STEPS = {"step01", "step02", "step03", "step04"}
MANIFEST_FIELDS = {
    "schema_version", "is_template", "run_id", "step_id", "operation",
    "method_id", "purpose", "status", "plan_version", "protocol_versions",
    "parent_run_ids", "started_at", "finished_at", "command_argv",
    "working_directory", "code", "inputs", "config", "environment",
    "outputs", "metrics", "validation", "exit_code", "failure",
    "reproduction", "notes_ref",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                                    allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def local_path(root, relative):
    if not isinstance(relative, str) or not relative:
        raise ValueError("Expected a nonempty project-relative reference")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Reference escapes the project: " + relative)
    return path


def validate_manifest(record):
    errors = []
    if not isinstance(record, dict):
        return ["manifest must be an object"]
    missing = MANIFEST_FIELDS - record.keys()
    if missing:
        errors.append("missing fields: " + ", ".join(sorted(missing)))
    if record.get("schema_version") != 1:
        errors.append("unsupported schema_version")
    if record.get("is_template") is not False:
        errors.append("template is not an experiment")
    for key in ("run_id", "operation", "purpose", "plan_version"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            errors.append(key + " must be a nonempty string")
    if record.get("step_id") not in STEPS:
        errors.append("invalid step_id")
    status = record.get("status")
    if status not in STATES:
        errors.append("invalid status")
    for key in ("parent_run_ids", "command_argv", "code", "inputs", "outputs"):
        if not isinstance(record.get(key), list):
            errors.append(key + " must be an array")
    for key in ("config", "environment", "metrics", "protocol_versions", "validation", "reproduction"):
        if not isinstance(record.get(key), dict):
            errors.append(key + " must be an object")
    if status in {"running", "completed", "failed", "interrupted"}:
        for key in ("started_at", "working_directory"):
            if not record.get(key):
                errors.append(key + " is required after execution starts")
        for key in ("command_argv", "code", "inputs", "config", "environment"):
            if not record.get(key):
                errors.append(key + " is required after execution starts")
    if status in {"completed", "failed", "interrupted"} and not record.get("finished_at"):
        errors.append("finished_at is required for a finished run")
    if status == "completed":
        if record.get("exit_code") != 0:
            errors.append("completed run must have exit_code 0")
        if not record.get("outputs"):
            errors.append("completed run requires outputs")
        validation = record.get("validation")
        if not isinstance(validation, dict) or validation.get("status") not in {"passed", "failed", "not_checked"}:
            errors.append("invalid validation status")
    if status in {"failed", "interrupted"} and not record.get("failure"):
        errors.append("failed/interrupted run requires failure details")
    for key in ("code", "inputs", "outputs"):
        entries = record.get(key)
        if not isinstance(entries, list):
            continue
        for item in entries:
            if not isinstance(item, dict):
                errors.append(key + " entry must be an object")
                continue
            required = {"id", "snapshot_ref", "sha256"} if key == "code" else {"id", "role", "version", "sha256", "storage"}
            if not required.issubset(item):
                errors.append(key + " entry missing " + ", ".join(sorted(required - item.keys())))
            for field in required - {"sha256"}:
                if not isinstance(item.get(field), str) or not item[field].strip():
                    errors.append(key + " entry has empty " + field)
            if item.get("sha256") is not None and not re.fullmatch(r"[a-fA-F0-9]{64}", str(item["sha256"])):
                errors.append(key + " entry has invalid sha256")
            if key == "code" and not item.get("sha256"):
                errors.append("code sha256 cannot be null")
            if key == "code" and not str(item.get("snapshot_ref", "")).replace("\\", "/").startswith("code_snapshot/"):
                errors.append("code must reference code_snapshot/")
            if key != "code" and item.get("storage") not in {"repository", "local_only"}:
                errors.append(key + " entry has invalid storage")
            if key != "code" and item.get("storage") == "local_only" and item.get("ref"):
                errors.append("local-only paths belong in local_data/paths.json")
            if key != "code" and item.get("storage") == "repository" and not item.get("ref"):
                errors.append("repository artifact requires ref")
            if item.get("sha256") is None and not item.get("fingerprint_missing_reason"):
                errors.append(key + " entry requires sha256 or fingerprint_missing_reason")
    return errors


def build_index(root):
    state = read_json(root / "research_state.json")
    records = []
    for step in state["steps"]:
        directory = local_path(root, step["readme"]).parent / "runs"
        if not directory.exists():
            continue
        for run in sorted(path for path in directory.iterdir() if path.is_dir()):
            manifest = run / "manifest.json"
            if manifest.exists():
                value = read_json(manifest)
                errors = validate_manifest(value)
                records.append({
                    "run_id": run.name, "step_id": step["id"],
                    "record_type": "manifest", "operation": value.get("operation"),
                    "status": value.get("status"), "manifest_ref": manifest.relative_to(root).as_posix(),
                    "parent_run_ids": value.get("parent_run_ids", []),
                    "record_check": "failed" if errors else "passed", "record_errors": errors,
                    "validation_status": value["validation"].get("status") if isinstance(value.get("validation"), dict) else None,
                    "reproduction_status": value["reproduction"].get("status") if isinstance(value.get("reproduction"), dict) else None,
                })
                continue
            # Old records remain unchanged. Their missing provenance is explicit.
            for filename, kind in (("sources.json", "source_check"), ("verification.json", "record_check")):
                evidence = run / filename
                if evidence.exists():
                    value = read_json(evidence)
                    records.append({
                        "run_id": run.name, "step_id": step["id"],
                        "record_type": "legacy_" + kind,
                        "operation": kind,
                        "status": "errors_reported" if value.get("errors") else "no_errors_reported",
                        "evidence_ref": evidence.relative_to(root).as_posix(),
                        "registered_after_execution": True,
                        "provenance": "partial", "model_experiment": False,
                    })
                    break
    return {"schema_version": 1, "generated_by": "research_tools/ai_records.py index",
            "records": records}


def check(root):
    errors = []
    state = read_json(root / "research_state.json")
    if state.get("schema_version") != 1:
        errors.append("research_state schema version is unsupported")
    if state.get("current_step") not in STEPS:
        errors.append("unknown current step")
    refs = list(state["documents"].values()) + [step["readme"] for step in state["steps"]]
    for ref in refs:
        if not local_path(root, ref).is_file():
            errors.append("missing state reference: " + ref)
    index = build_index(root)
    saved = read_json(root / "experiment_index.json")
    if index != saved:
        errors.append("experiment_index.json is stale; run index")
    ids = [item["run_id"] for item in index["records"]]
    if len(ids) != len(set(ids)):
        errors.append("duplicate run IDs")
    for item in index["records"]:
        if item.get("record_errors"):
            errors.extend(item["run_id"] + ": " + error for error in item["record_errors"])
        for parent in item.get("parent_run_ids", []):
            if parent not in ids:
                errors.append(item["run_id"] + ": unknown parent " + parent)
        if item["record_type"] != "manifest":
            continue
        if item.get("record_errors"):
            continue
        manifest_path = local_path(root, item["manifest_ref"])
        value = read_json(manifest_path)
        if value.get("run_id") != item["run_id"] or value.get("step_id") != item["step_id"]:
            errors.append(item["run_id"] + ": manifest ID or step does not match location")
        for code in value.get("code", []):
            snapshot = local_path(root, str((manifest_path.parent.relative_to(root) / code["snapshot_ref"]).as_posix()))
            if not snapshot.is_file() or hashlib.sha256(snapshot.read_bytes()).hexdigest() != code["sha256"]:
                errors.append(item["run_id"] + ": missing or changed code snapshot")
        for artifact in value["inputs"] + value["outputs"]:
            if artifact["storage"] != "repository":
                continue
            path = local_path(root, artifact["ref"])
            if not path.is_file():
                errors.append(item["run_id"] + ": missing artifact " + artifact["id"])
            elif artifact["sha256"] and hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
                errors.append(item["run_id"] + ": changed artifact " + artifact["id"])
    parents = {item["run_id"]: item.get("parent_run_ids", []) for item in index["records"]}
    def visit(run_id, path):
        if run_id in path:
            errors.append("cyclic parent references: " + run_id)
            return
        for parent in parents.get(run_id, []):
            visit(parent, path | {run_id})
    for run_id in parents:
        visit(run_id, set())
    return {"schema_version": 1, "records_checked": len(index["records"]),
            "errors": errors, "scope": "record consistency, not scientific validity or model reproduction"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("index", "context", "check", "validate-manifest"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.action == "index":
        value = build_index(root)
        write_json(root / "experiment_index.json", value)
    elif args.action == "context":
        value = {"state": read_json(root / "research_state.json"),
                 "experiments": read_json(root / "experiment_index.json")}
    elif args.action == "check":
        value = check(root)
    else:
        if args.manifest is None:
            parser.error("--manifest is required")
        value = {"errors": validate_manifest(read_json(args.manifest))}
    if args.output:
        if args.output.exists():
            parser.error("Output exists; use a new record location")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        write_json(args.output, value)
    print(json.dumps(value, ensure_ascii=True, allow_nan=False))
    return 1 if value.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
