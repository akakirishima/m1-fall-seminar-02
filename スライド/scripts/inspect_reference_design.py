"""Inspect selected reference slide geometry and extract only their picture assets."""
import argparse
import json
import posixpath
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}


def design(archive, member, number, assets):
    root = ET.fromstring(archive.read(member))
    relations_path = posixpath.join(posixpath.dirname(member), "_rels", posixpath.basename(member) + ".rels")
    relations = {r.attrib["Id"]: r.attrib["Target"] for r in ET.fromstring(archive.read(relations_path))}
    result = {"number": number, "text": [], "pictures": [], "tables": []}
    for shape in root.findall(".//p:sp", NS):
        paragraphs = shape.findall("p:txBody/a:p", NS)
        text = " / ".join("".join(t.text or "" for t in p.findall(".//a:t", NS)) for p in paragraphs)
        if not text.strip(" / "):
            continue
        transform = shape.find("p:spPr/a:xfrm", NS)
        position = {c.tag.rsplit("}", 1)[-1]: c.attrib for c in transform} if transform is not None else {}
        runs = []
        for run in shape.findall(".//a:r", NS):
            properties = run.find("a:rPr", NS)
            runs.append({"text": run.findtext("a:t", default="", namespaces=NS),
                         "attributes": properties.attrib if properties is not None else {},
                         "properties": ET.tostring(properties, encoding="unicode") if properties is not None else ""})
        result["text"].append({"text": text, "position": position, "runs": runs})
    for index, picture in enumerate(root.findall(".//p:pic", NS), 1):
        transform = picture.find("p:spPr/a:xfrm", NS)
        blip = picture.find("p:blipFill/a:blip", NS)
        if transform is None or blip is None:
            continue
        target = relations[blip.attrib[f"{{{NS['r']}}}embed"]]
        source = posixpath.normpath(posixpath.join(posixpath.dirname(member), target))
        name = f"slide-{number:03d}-picture-{index:02d}{Path(source).suffix}"
        if number in (1, 7):
            (assets / name).write_bytes(archive.read(source))
        result["pictures"].append({"asset": name, "transform": transform.attrib, "position": {c.tag.rsplit("}", 1)[-1]: c.attrib for c in transform},
                                   "crop": ET.tostring(picture.find("p:blipFill", NS), encoding="unicode")})
    for frame in root.findall(".//p:graphicFrame", NS):
        table = frame.find(".//a:tbl", NS)
        if table is not None:
            result["tables"].append(ET.tostring(frame, encoding="unicode"))
    return result


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("inspection", type=Path)
    parser.add_argument("assets", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.assets.mkdir(parents=True, exist_ok=True)
    listing = json.loads(args.inspection.read_text(encoding="utf-8"))
    with ZipFile(args.source) as archive:
        result = [design(archive, listing["slides"][n - 1]["xml_member"], n, args.assets)
                  for n in (1, 2, 7, 15, 16, 18, 20, 46)]
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    for slide in result:
        print(f"Slide {slide['number']}")
        for item in slide["text"]:
            sizes = sorted({r["attributes"].get("sz", "inherited") for r in item["runs"]})
            print(json.dumps({"text": item["text"], "sizes": sizes, "position": item["position"]}, ensure_ascii=False))
        print(json.dumps({"pictures": slide["pictures"]}, ensure_ascii=False))
        for table in slide["tables"]:
            print(table)
