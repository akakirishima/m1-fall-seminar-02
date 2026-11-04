"""Record official OSS/model metadata without installing packages or weights."""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


REPOSITORIES = [
    "OthmanAdi/planning-with-files",
    "ZIB-IOL/The-Agentic-Researcher",
    "karpathy/autoresearch",
    "K-Dense-AI/scientific-agent-skills",
    "Orchestra-Research/AI-Research-SKILLs",
    "pytorch/pytorch",
    "pytorch/vision",
    "huggingface/transformers",
    "huggingface/peft",
    "huggingface/accelerate",
    "QwenLM/Qwen3-VL",
    "bitsandbytes-foundation/bitsandbytes",
]
MODELS = ["Qwen/Qwen3.5-4B", "Qwen/Qwen3-VL-4B-Instruct"]


def request_json(url):
    request = Request(url, headers={"User-Agent": "infant-intervention-source-check"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repository", action="append", help="Check only these repositories (repeatable).")
    parser.add_argument("--skip-models", action="store_true", help="Do not query model metadata.")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; choose a new run directory.")
    observed = datetime.now(timezone(timedelta(hours=9))).isoformat()
    record = {
        "checked_at": observed,
        "purpose": "Official source metadata; not installed-package versions or runtime validation",
        "repositories": [],
        "models": [],
        "errors": [],
    }
    for name in args.repository or REPOSITORIES:
        api_url = "https://api.github.com/repos/" + name
        try:
            metadata = request_json(api_url)
            branch = metadata["default_branch"]
            commit = request_json(api_url + "/commits/" + quote(branch, safe=""))
            revision = commit["sha"]
            record["repositories"].append({
                "name": metadata["full_name"],
                "url": metadata["html_url"],
                "api_url": api_url,
                "default_branch": branch,
                "observed_revision": revision,
                "revision_url": metadata["html_url"] + "/tree/" + revision,
                "license_metadata": (metadata.get("license") or {}).get("spdx_id"),
                "pushed_at": metadata.get("pushed_at"),
            })
            print("OK repository", name)
        except (HTTPError, URLError, KeyError, ValueError) as exc:
            record["errors"].append({"source": name, "error": str(exc)})
            print("FAILED repository", name, str(exc))
    for name in ([] if args.skip_models else MODELS):
        api_url = "https://huggingface.co/api/models/" + name
        try:
            metadata = request_json(api_url)
            revision = metadata["sha"]
            record["models"].append({
                "name": metadata["id"],
                "url": "https://huggingface.co/" + name,
                "api_url": api_url,
                "observed_revision": revision,
                "revision_url": "https://huggingface.co/" + name + "/tree/" + revision,
                "license_metadata": (metadata.get("cardData") or {}).get("license"),
            })
            print("OK model", name)
        except (HTTPError, URLError, KeyError, ValueError) as exc:
            record["errors"].append({"source": name, "error": str(exc)})
            print("FAILED model", name, str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(record, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print("Saved", args.output)
    return 1 if record["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
