"""Read slide order and text from a reference PPTX without modifying it."""
import argparse
import hashlib
import json
import posixpath
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def inspect(source: Path) -> dict:
    with ZipFile(source) as archive:
        presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
        relations = ET.fromstring(archive.read("ppt/_rels/presentation.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in relations}
        size = presentation.find("p:sldSz", NS)
        slides = []
        for number, item in enumerate(presentation.findall("p:sldIdLst/p:sldId", NS), 1):
            target = targets[item.attrib[f"{{{NS['r']}}}id"]]
            member = (target.lstrip("/") if target.startswith("/") else
                      posixpath.normpath(posixpath.join("ppt", target)))
            root = ET.fromstring(archive.read(member))
            paragraphs = ["".join(t.text or "" for t in paragraph.findall(".//a:t", NS))
                          for paragraph in root.findall(".//a:p", NS)]
            paragraphs = [line for line in paragraphs if line.strip()]
            shapes = []
            for shape in root.findall(".//p:sp", NS):
                text = ["".join(t.text or "" for t in para.findall(".//a:t", NS))
                        for para in shape.findall("p:txBody/a:p", NS)]
                if not any(text):
                    continue
                transform = shape.find("p:spPr/a:xfrm", NS)
                position = ({part.tag.rsplit("}", 1)[-1]: part.attrib
                             for part in transform} if transform is not None else {})
                shapes.append({"paragraphs": text, "position": position})
            slides.append({"number": number, "xml_member": member,
                           "paragraphs": paragraphs, "shapes": shapes})
    digest = hashlib.sha256()
    with source.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"source_name": source.name,
            "sha256": digest.hexdigest(),
            "slide_size_emu": size.attrib if size is not None else None,
            "slides": slides}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = inspect(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"slide_count": len(result["slides"]),
                      "slide_size_emu": result["slide_size_emu"],
                      "sha256": result["sha256"]}, ensure_ascii=False))
    for slide in result["slides"]:
        preview = " / ".join(slide["paragraphs"])
        print(f"{slide['number']:03d}: {preview[:240]}")
