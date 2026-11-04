"""Compare PowerPoint renderings of the same deck before and after moving parts to the master."""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops

parser = argparse.ArgumentParser()
parser.add_argument("before", type=Path)
parser.add_argument("after", type=Path)
parser.add_argument("report", type=Path)
parser.add_argument("--threshold", type=int, default=40, help="per-channel difference that counts as changed")
args = parser.parse_args()
records = []
for path in sorted(args.before.glob("slide-*.png")):
    with Image.open(path) as first, Image.open(args.after / path.name) as second:
        first, second = first.convert("RGB"), second.convert("RGB")
        if first.size != second.size:
            records.append({"page": path.name, "error": "size differs"})
            continue
        difference = ImageChops.difference(first, second).convert("L").point(lambda value: 255 if value >= args.threshold else 0)
        changed = sum(1 for value in difference.get_flattened_data() if value)
        records.append({"page": path.name, "changed_pixels": changed, "changed_box": difference.getbbox()})
worst = sorted(records, key=lambda item: item.get("changed_pixels", 10**9), reverse=True)[:8]
args.report.write_text(json.dumps({"threshold": args.threshold, "pages": records}, indent=2), encoding="utf-8")
print(json.dumps({"pages": len(records), "pages_with_changes": sum(1 for item in records if item.get("changed_pixels")), "worst": worst}))
