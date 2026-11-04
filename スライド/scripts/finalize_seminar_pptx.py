"""Correct Slidev's negative title offsets in an editable export, preserving the raw file."""
import argparse
import json
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as ET

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("report", type=Path)
args = parser.parse_args()
if args.source.resolve() == args.output.resolve():
    raise ValueError("Keep the raw export separate from the final output")
changes = []
removed_overrides = []
args.output.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(args.source) as source, ZipFile(args.output, "w") as output:
    parts = set(source.namelist())
    for entry in source.infolist():
        content = source.read(entry.filename)
        if entry.filename == "[Content_Types].xml":
            root = ET.fromstring(content)
            for item in list(root):
                part = item.get("PartName", "").lstrip("/")
                # Slidev declares one master per page but emits only the shared master.
                # Remove only declarations of masters that do not exist in the ZIP.
                if part.startswith("ppt/slideMasters/slideMaster") and part not in parts:
                    root.remove(item)
                    removed_overrides.append(part)
            content = ET.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
        if entry.filename.startswith("ppt/slides/slide") and entry.filename.endswith(".xml"):
            root = ET.fromstring(content)
            for shape in root.findall("p:cSld/p:spTree/p:sp", NS):
                offset = shape.find("p:spPr/a:xfrm/a:off", NS)
                text = "".join(shape.xpath(".//a:t/text()", namespaces=NS))
                if offset is None or not text:
                    continue
                old_y = int(offset.get("y"))
                if old_y < 0 and abs(int(offset.get("x")) - 495300) < 100:
                    # 9525 EMU per CSS px; observed baseline offset differs for the larger agenda title.
                    delta = 13 * 9525 if text == "もくじ" else 8 * 9525
                    new_y = old_y + delta
                    if new_y < 0:
                        raise ValueError(f"Unexpected title position: {entry.filename}")
                    offset.set("y", str(new_y))
                    changes.append({"slide_part": entry.filename, "title": text,
                                    "before_y_emu": old_y, "after_y_emu": new_y})
            content = ET.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
        output.writestr(entry, content)
args.report.parent.mkdir(parents=True, exist_ok=True)
args.report.write_text(json.dumps({"raw": str(args.source), "final": str(args.output),
                                  "title_position_corrections": changes,
                                  "removed_nonexistent_master_declarations": removed_overrides}, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"corrected_titles": len(changes), "removed_unused_declarations": len(removed_overrides),
                  "output": str(args.output)}, ensure_ascii=True))
