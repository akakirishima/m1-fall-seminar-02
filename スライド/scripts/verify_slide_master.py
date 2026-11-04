"""Verify that the rule and footer live in the master and layouts, not on the slides.

Compares a pre-master export with the final PPTX: each content slide keeps its chapter,
page field and all other text.
"""
import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile

from lxml import etree as ET

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"p": P, "a": A, "r": R}
PX = 9525
CHAPTERS = ["研究背景", "課題", "取り組み", "実験と結果", "まとめ"]
FOOTER_TOP = 863 * PX

parser = argparse.ArgumentParser()
parser.add_argument("before", type=Path)
parser.add_argument("after", type=Path)
parser.add_argument("report", type=Path)
parser.add_argument("--skip-body-text", action="store_true",
                    help="for the final file, where table text has moved into native tables")
args = parser.parse_args()
errors = []


def slide_parts(archive):
    root = ET.fromstring(archive.read("ppt/presentation.xml"))
    rels = {item.get("Id"): item.get("Target") for item in ET.fromstring(archive.read("ppt/_rels/presentation.xml.rels"))}
    return ["ppt/" + rels[item.get(f"{{{R}}}id")] for item in root.findall("p:sldIdLst/p:sldId", NS)]


def in_footer(shape):
    offset = shape.find("p:spPr/a:xfrm/a:off", NS)
    return offset is not None and int(offset.get("y")) >= FOOTER_TOP


def body_texts(root):
    # Shapes above the footer; table cells are checked by the table verifier.
    found = []
    for shape in root.findall("p:cSld/p:spTree/p:sp", NS):
        text = "".join(shape.xpath(".//a:t/text()", namespaces=NS))
        if text and not in_footer(shape) and not shape.xpath(".//p:ph", namespaces=NS):
            found.append(text)
    return sorted(found)


def layout_of(archive, part):
    directory, name = part.rsplit("/", 1)
    for item in ET.fromstring(archive.read(f"{directory}/_rels/{name}.rels")):
        if item.get("Type").endswith("/slideLayout"):
            target = "ppt/slideLayouts/" + item.get("Target").rsplit("/", 1)[1]
            return target
    return None


with ZipFile(args.before) as before, ZipFile(args.after) as after:
    before_parts, after_parts = slide_parts(before), slide_parts(after)
    if len(before_parts) != len(after_parts):
        errors.append("slide count changed")
    masters = [name for name in after.namelist() if re.fullmatch(r"ppt/slideMasters/slideMaster\d+\.xml", name)]
    if len(masters) != 1:
        errors.append(f"expected one master, found {len(masters)}")
    master = ET.fromstring(after.read(masters[0]))
    master_text = "".join(master.xpath("p:cSld/p:spTree//a:t/text()", namespaces=NS))
    for needed in ("Hiroki Matsumoto,", "University of Miyazaki"):
        if needed not in master_text:
            errors.append(f"master lacks {needed}")
    if not master.xpath("p:cSld/p:spTree/p:sp/p:spPr/a:gradFill", namespaces=NS):
        errors.append("master lacks the gradient rule")
    if not master.xpath('p:cSld/p:spTree/p:sp/p:nvSpPr/p:nvPr/p:ph[@type="sldNum"]', namespaces=NS):
        errors.append("master lacks the slide number placeholder")

    records = []
    for number, (old_part, new_part) in enumerate(zip(before_parts, after_parts), 1):
        old = ET.fromstring(before.read(old_part))
        new = ET.fromstring(after.read(new_part))
        old_chapter = [shape for shape in old.findall("p:cSld/p:spTree/p:sp", NS)
                       if in_footer(shape) and "".join(shape.xpath(".//a:t/text()", namespaces=NS)) in CHAPTERS
                       and "FFFFFF" in [v.upper() for v in shape.xpath(".//a:rPr/a:solidFill/a:srgbClr/@val", namespaces=NS)]]
        layout_part = layout_of(after, new_part)
        layout = ET.fromstring(after.read(layout_part))
        layout_name = layout.find("p:cSld", NS).get("name")
        white = [text for shape in layout.findall("p:cSld/p:spTree/p:sp", NS)
                 for text in ["".join(shape.xpath(".//a:t/text()", namespaces=NS))]
                 if text in CHAPTERS and "FFFFFF" in [v.upper() for v in shape.xpath(".//a:rPr/a:solidFill/a:srgbClr/@val", namespaces=NS)]]
        expected = ["".join(shape.xpath(".//a:t/text()", namespaces=NS)) for shape in old_chapter]
        if white != expected:
            errors.append(f"Slide {number}: current chapter {expected} became {white}")
        leftovers = [shape for shape in new.findall("p:cSld/p:spTree/p:sp", NS) if in_footer(shape)]
        if leftovers:
            errors.append(f"Slide {number}: {len(leftovers)} footer shapes are still on the slide")
        pictures = new.findall("p:cSld/p:spTree/p:pic", NS)
        thin = [p for p in pictures if int(p.find("p:spPr/a:xfrm/a:ext", NS).get("cy")) <= 8 * PX + PX]
        if thin:
            errors.append(f"Slide {number}: a rule picture is still on the slide")
        for shape in new.findall("p:cSld/p:spTree/p:sp", NS):
            ext = shape.find("p:spPr/a:xfrm/a:ext", NS)
            if ext is not None and int(ext.get("cx")) >= 1190 * PX and int(ext.get("cy")) >= 890 * PX:
                errors.append(f"Slide {number}: full-page background shape remains")
        fields = new.xpath('.//p:ph[@type="sldNum"]/ancestor::p:sp//a:fld[@type="slidenum"]/a:t/text()', namespaces=NS)
        is_content = bool(old_chapter) or layout_name.startswith("本文_")
        if is_content and fields != [str(number)]:
            errors.append(f"Slide {number}: page field is {fields}")
        if not is_content and fields:
            errors.append(f"Slide {number}: unexpected page field")
        old_content, new_content = body_texts(old), body_texts(new)
        if not args.skip_body_text and old_content != new_content:
            missing = [t for t in old_content if t not in new_content][:3]
            added = [t for t in new_content if t not in old_content][:3]
            errors.append(f"Slide {number}: text changed, missing {missing}, added {added}")
        records.append({"slide": number, "layout": layout_name, "page_field": fields[0] if fields else None})

report = {"slides": len(records), "records": records, "errors": errors,
          "scope": "master and layout placement, current chapter, page field, slide text outside tables"}
args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"slides": len(records), "errors": len(errors), "first_errors": errors[:5]}, ensure_ascii=True))
raise SystemExit(bool(errors))
