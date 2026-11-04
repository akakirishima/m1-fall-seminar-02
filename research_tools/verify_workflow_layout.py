"""Verify registered work folders and links without reading private data."""

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import ai_records


def verify(root):
    state = ai_records.read_json(root / "research_state.json")
    packages = state["work_packages"]
    by_id = {p["id"]: p for p in packages}
    errors = []
    if len(by_id) != len(packages):
        errors.append("duplicate package IDs")
    if state["current_work_package"] not in by_id:
        errors.append("unknown current work package")
    visited = set()

    def visit(package_id, visiting):
        if package_id in visiting:
            errors.append("cyclic package dependency: " + package_id)
            return
        if package_id in visited:
            return
        if package_id not in by_id:
            errors.append("unknown package dependency: " + package_id)
            return
        for dependency in by_id[package_id]["depends_on"]:
            visit(dependency, visiting | {package_id})
        visited.add(package_id)

    refs = set(state["documents"].values())
    for step in state["steps"]:
        refs.add(step["readme"])
        expected = {p["id"] for p in packages if p["step_id"] == step["id"]}
        if set(step["work_package_ids"]) != expected:
            errors.append("step/package mismatch: " + step["id"])
    for package in packages:
        visit(package["id"], set())
        refs.add(package["readme"])
        folder = ai_records.local_path(root, package["readme"]).parent
        for name in ("scripts", "configs", "runs"):
            if not (folder / name).is_dir():
                errors.append("missing task directory: " + (folder / name).relative_to(root).as_posix())
        if ai_records.local_path(root, package["runs_dir"]) != folder / "runs":
            errors.append("task runs path mismatch: " + package["id"])
    refs.update(m["readme"] for m in state["methods"] if m.get("readme"))
    links = 0
    for ref in sorted(refs):
        path = ai_records.local_path(root, ref)
        if not path.is_file():
            errors.append("missing document: " + ref)
            continue
        if path.suffix != ".md":
            continue
        content = path.read_text(encoding="utf-8-sig")
        if re.search(r"^(<<<<<<<|=======|>>>>>>>)", content, re.M):
            errors.append("unresolved conflict: " + ref)
        for match in re.finditer(r"\[[^\]\n]+\]\(([^)\n]+)\)", content):
            target = match.group(1).strip().strip("<>")
            if not target or target.startswith("#") or urlsplit(target).scheme:
                continue
            links += 1
            if not (path.parent / unquote(target.split("#", 1)[0])).exists():
                errors.append("missing link in " + ref + ": " + target)
    return {"scope": "work-folder and document consistency, not model verification",
            "packages_checked": len(packages), "documents_checked": len(refs),
            "local_links_checked": links, "errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(report, ensure_ascii=True))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
