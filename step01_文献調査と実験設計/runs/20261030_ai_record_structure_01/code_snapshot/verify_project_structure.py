"""Check the newly authored project documents and local links only."""

import argparse
import ast
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit


DOCUMENTS = [
    "README.md", "AGENTS.md", "研究全体像.md", "方針変更履歴.md",
    "共通/使用OSSと出典.md", "共通/ラベル付け規則.md", "共通/評価方法.md",
    "共通/実験記録の運用.md", "共通/データ一覧と分割/README.md",
    "共通/AI向け記録形式.md",
    "templates/日報テンプレート.md", "templates/実行結果テンプレート.md",
    "日報/2026-10-30.md",
    "step01_文献調査と実験設計/README.md",
    "step02_正解データ作成/README.md",
    "step03_各手法の実装と実験/README.md",
    "step04_総合比較と考察/README.md",
    "step01_文献調査と実験設計/runs/20261030_oss_sources_01/実行結果.md",
    "調査/VLM候補比較と研究室PCでの選定_20261030.md",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; choose a new run directory.")
    errors = []
    links_checked = 0
    for name in DOCUMENTS:
        path = args.root / name
        if not path.is_file():
            errors.append({"file": name, "error": "Missing document"})
            continue
        content = path.read_text(encoding="utf-8-sig")
        if "\ufffd" in content:
            errors.append({"file": name, "error": "Replacement character in text"})
        for match in re.finditer(r"\[[^\]\n]+\]\(([^)\n]+)\)", content):
            target = match.group(1).strip().strip("<>")
            if not target or target.startswith("#") or urlsplit(target).scheme:
                continue
            relative = unquote(target.split("#", 1)[0])
            links_checked += 1
            if not (path.parent / relative).exists():
                errors.append({"file": name, "error": "Missing link target", "target": target})
    for name in (
        "step02_正解データ作成/scripts", "step02_正解データ作成/runs",
        "step03_各手法の実装と実験/scripts", "step03_各手法の実装と実験/configs",
        "step03_各手法の実装と実験/runs", "step04_総合比較と考察/scripts",
        "step04_総合比較と考察/runs",
    ):
        if not (args.root / name).is_dir():
            errors.append({"file": name, "error": "Missing directory"})
    for name in ("verify_oss_sources.py", "verify_project_structure.py"):
        path = args.root / "step01_文献調査と実験設計/scripts" / name
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    sources = json.loads((args.root / "step01_文献調査と実験設計/runs/20261030_oss_sources_01/sources.json").read_text(encoding="utf-8"))
    if len(sources["repositories"]) != 12 or len(sources["models"]) != 2 or sources["errors"]:
        errors.append({"error": "Unexpected source-check counts or errors"})
    report = {
        "checked_at": datetime.now(timezone(timedelta(hours=9))).isoformat(),
        "scope": "New project documents and edited candidate memo; not historical slide assets or model experiments",
        "documents_checked": len(DOCUMENTS),
        "local_links_checked": links_checked,
        "repository_sources": len(sources["repositories"]),
        "model_sources": len(sources["models"]),
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(report, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print(json.dumps(report, ensure_ascii=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
