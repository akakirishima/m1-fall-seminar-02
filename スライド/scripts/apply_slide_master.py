"""Move the title rule and footer band from every slide into the slide master and layouts.

Slidev writes these parts onto each slide and leaves the master empty. This keeps the
source export unchanged and stops on any slide that does not match the expected shapes.
"""
import argparse
import copy
import json
import posixpath
import re
from pathlib import Path
from zipfile import ZipFile

from lxml import etree as ET

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
NS = {"p": P, "a": A, "r": R}
LAYOUT_TYPE = f"{R}/slideLayout"
MASTER_TYPE = f"{R}/slideMaster"
LAYOUT_CONTENT = "application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"
PX = 9525

CHAPTERS = ["研究背景", "課題", "取り組み", "実験と結果", "まとめ"]
CREDITS = ["Hiroki Matsumoto,", "University of Miyazaki"]
BACKGROUND = (0, 0, 1200, 900)
BAND = (0, 863, 1200, 37)
PAGE_BOX = (1130, 863, 70, 37)
TITLE_RULE = (35, 67, 1134, 8)
COVER_RULE = (35, 510, 1153, 8)
DIVIDER_RULE = (52, 482, 1096, 8)
RULE_COLORS = ("F27509", "FFEADC")
COVER_LAYOUT = "表紙"
DIVIDER_LAYOUT = "章の扉"
SLIDE_NUMBER_PH = {"type": "sldNum", "sz": "quarter", "idx": "12"}

parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("report", type=Path)
args = parser.parse_args()
if args.source.resolve() == args.output.resolve():
    raise ValueError("Keep the source export separate from the output")


def q(namespace, name):
    return f"{{{namespace}}}{name}"


def box(shape):
    off = shape.find("p:spPr/a:xfrm/a:off", NS)
    ext = shape.find("p:spPr/a:xfrm/a:ext", NS)
    if off is None or ext is None:
        return None
    return tuple(round(int(value) / PX) for value in
                 (off.get("x"), off.get("y"), ext.get("cx"), ext.get("cy")))


def text_of(shape):
    return "".join(shape.xpath(".//a:t/text()", namespaces=NS))


def color_of(shape):
    colors = shape.xpath(".//a:rPr/a:solidFill/a:srgbClr/@val", namespaces=NS)
    return colors[0].upper() if colors else None


def element(xml):
    return ET.fromstring(f'<root xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}">{xml}</root>')[0]


def gradient_stops(count=9):
    # PowerPoint blends colors differently from CSS, so give the CSS colors at each stop.
    first, last = (tuple(int(color[i:i + 2], 16) for i in (0, 2, 4)) for color in RULE_COLORS)
    stops = []
    for index in range(count):
        ratio = index / (count - 1)
        color = "".join(f"{round(a + (b - a) * ratio):02X}" for a, b in zip(first, last))
        stops.append(f'<a:gs pos="{round(ratio * 100000)}"><a:srgbClr val="{color}"/></a:gs>')
    return "".join(stops)


def rule_shape(raw_box, shape_id):
    x, y, w, h = (value * PX for value in raw_box)
    return element(f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="線"/><p:cNvSpPr/><p:nvPr userDrawn="1"/></p:nvSpPr>
<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>
<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 50000"/></a:avLst></a:prstGeom>
<a:gradFill rotWithShape="1"><a:gsLst>{gradient_stops()}</a:gsLst><a:lin ang="0" scaled="0"/></a:gradFill>
<a:ln><a:noFill/></a:ln></p:spPr></p:sp>""")


def number_placeholder(shape_id, xfrm, style):
    x, y, w, h = (value * PX for value in PAGE_BOX)
    position = f'<a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>' if xfrm else ""
    body = '<a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr"/>' if style else "<a:bodyPr/>"
    styles = ('<a:lstStyle><a:lvl1pPr algn="ctr"><a:defRPr sz="1950" b="1"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
              '<a:latin typeface="Arial"/><a:ea typeface="Arial"/><a:cs typeface="Arial"/></a:defRPr></a:lvl1pPr></a:lstStyle>') if style else "<a:lstStyle/>"
    return element(f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="ページ番号"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
<p:nvPr><p:ph type="sldNum" sz="quarter" idx="12"/></p:nvPr></p:nvSpPr><p:spPr>{position}</p:spPr>
<p:txBody>{body}{styles}<a:p><a:fld id="{{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}}" type="slidenum"><a:rPr lang="ja-JP"/><a:t>‹#›</a:t></a:fld><a:endParaRPr lang="ja-JP"/></a:p></p:txBody></p:sp>""")


def copied(shape, shape_id, name):
    result = copy.deepcopy(shape)
    properties = result.find("p:nvSpPr/p:cNvPr", NS)
    properties.set("id", str(shape_id))
    properties.set("name", name)
    result.find("p:nvSpPr/p:nvPr", NS).set("userDrawn", "1")
    return result


def layout_xml(name, shapes, show_master):
    tree = ('<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
            '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>')
    flag = "" if show_master else ' showMasterSp="0"'
    root = ET.fromstring(f"""<p:sldLayout xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{P}" preserve="1" userDrawn="1"{flag}>
<p:cSld name="{name}"><p:spTree>{tree}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>""")
    spTree = root.find("p:cSld/p:spTree", NS)
    for shape in shapes:
        spTree.append(shape)
    return serialize(root)


def serialize(root):
    return ET.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def relationships(pairs):
    root = ET.Element(q(REL, "Relationships"), nsmap={None: REL})
    for rel_id, rel_type, target in pairs:
        ET.SubElement(root, q(REL, "Relationship"), Id=rel_id, Type=rel_type, Target=target)
    return serialize(root)


with ZipFile(args.source) as source:
    parts = {entry.filename: source.read(entry.filename) for entry in source.infolist()}
    entries = list(source.infolist())

presentation = ET.fromstring(parts["ppt/presentation.xml"])
pres_rels = {item.get("Id"): item.get("Target") for item in ET.fromstring(parts["ppt/_rels/presentation.xml.rels"])}
slide_parts = ["ppt/" + pres_rels[item.get(q(R, "id"))]
               for item in presentation.findall("p:sldIdLst/p:sldId", NS)]

slides = []
samples = {}
for number, part in enumerate(slide_parts, 1):
    root = ET.fromstring(parts[part])
    tree = root.find("p:cSld/p:spTree", NS)
    found = {"chapters": {}, "credits": {}}
    errors = []
    for shape in tree:
        tag = ET.QName(shape).localname
        if tag not in ("sp", "pic"):
            continue
        where = box(shape)
        text = text_of(shape)
        if where == BACKGROUND and tag == "sp" and not text:
            found["background"] = shape
        elif where in (TITLE_RULE, COVER_RULE, DIVIDER_RULE) and tag == "pic":
            found.setdefault("rule", []).append((where, shape))
        elif where == BAND and tag == "sp" and not text:
            found["band"] = shape
        elif where == PAGE_BOX and tag == "sp" and not text:
            found["page_box"] = shape
        elif where is not None and tag == "sp" and where[1] >= 863:
            if text in CHAPTERS:
                found["chapters"][text] = shape
            elif text in CREDITS:
                found["credits"][text] = shape
            elif text.isdigit():
                found["number"] = shape
            else:
                errors.append(f"unexpected footer shape {text!r} at {where}")
    rules = found.get("rule", [])
    if "background" not in found:
        errors.append("no background shape")
    if len(rules) != 1:
        errors.append(f"expected one rule, found {len(rules)}")
    kind = {TITLE_RULE: "content", COVER_RULE: "cover", DIVIDER_RULE: "divider"}.get(rules[0][0]) if len(rules) == 1 else None
    has_footer = any(key in found for key in ("band", "page_box", "number")) or found["chapters"] or found["credits"]
    current = None
    if kind == "content":
        if not all(key in found for key in ("band", "page_box", "number")):
            errors.append("footer parts are missing")
        if set(found["chapters"]) != set(CHAPTERS) or set(found["credits"]) != set(CREDITS):
            errors.append("chapter or credit text does not match")
        if text_of(found.get("number", tree)) != str(number):
            errors.append("page number text does not match the slide position")
        white = [name for name, shape in found["chapters"].items() if color_of(shape) == "FFFFFF"]
        if len(white) > 1:
            errors.append(f"more than one current chapter: {white}")
        current = white[0] if white else None
        samples.setdefault(current, found)
    elif has_footer:
        errors.append("cover or divider has footer parts")
    if errors:
        raise SystemExit(f"Slide {number}: " + "; ".join(errors))
    slides.append({"number": number, "part": part, "root": root, "tree": tree, "found": found,
                   "kind": kind, "chapter": current})

content_sample = next(iter(samples.values()))
ordered = [name for name in CHAPTERS if name in samples] + ([None] if None in samples else [])
layouts = []
for name in ordered:
    label = f"本文_{name}" if name else "本文_章なし"
    shapes = [copied(samples[name]["chapters"][chapter], 2 + index, f"章_{chapter}")
              for index, chapter in enumerate(CHAPTERS)]
    shapes.append(number_placeholder(2 + len(CHAPTERS), xfrm=False, style=False))
    layouts.append({"key": ("content", name), "name": label, "xml": layout_xml(label, shapes, True)})
layouts.append({"key": ("cover", None), "name": COVER_LAYOUT, "xml": layout_xml(COVER_LAYOUT, [rule_shape(COVER_RULE, 2)], False)})
layouts.append({"key": ("divider", None), "name": DIVIDER_LAYOUT, "xml": layout_xml(DIVIDER_LAYOUT, [rule_shape(DIVIDER_RULE, 2)], False)})
layout_part = {layout["key"]: f"ppt/slideLayouts/slideLayout{index}.xml" for index, layout in enumerate(layouts, 1)}

output_parts = {}
removed_images = set()
kept_rules = 0
report_slides = []
for slide in slides:
    found, tree, root = slide["found"], slide["tree"], slide["root"]
    removal = [found["background"], found["rule"][0][1]]
    if slide["kind"] == "content":
        removal += [found["band"], found["page_box"], found["number"]]
        removal += list(found["chapters"].values()) + list(found["credits"].values())
    rule_rel = found["rule"][0][1].find("p:blipFill/a:blip", NS).get(q(R, "embed"))
    for shape in removal:
        tree.remove(shape)
    background = root.find("p:cSld/p:bg", NS)
    if background is not None:
        root.find("p:cSld", NS).remove(background)
    if slide["kind"] == "content":
        next_id = max(int(value) for value in root.xpath(".//p:cNvPr/@id", namespaces=NS)) + 1
        number_shape = element(f"""<p:sp><p:nvSpPr><p:cNvPr id="{next_id}" name="ページ番号"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
<p:nvPr><p:ph type="sldNum" sz="quarter" idx="12"/></p:nvPr></p:nvSpPr><p:spPr/>
<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:fld id="{{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}}" type="slidenum"><a:rPr lang="ja-JP"/><a:t>{slide['number']}</a:t></a:fld><a:endParaRPr lang="ja-JP"/></a:p></p:txBody></p:sp>""")
        tree.append(number_shape)
    output_parts[slide["part"]] = serialize(root)

    directory, name = posixpath.split(slide["part"])
    rels_part = f"{directory}/_rels/{name}.rels"
    rels = ET.fromstring(parts[rels_part])
    target = layout_part[(slide["kind"], slide["chapter"])]
    remaining = serialize(root).decode("utf-8")
    for item in list(rels):
        if item.get("Type") == LAYOUT_TYPE:
            item.set("Target", posixpath.relpath(target, directory))
        elif item.get("Id") == rule_rel and f'"{rule_rel}"' not in remaining:
            removed_images.add(posixpath.normpath(posixpath.join(directory, item.get("Target"))))
            rels.remove(item)
    output_parts[rels_part] = serialize(rels)
    label = next(layout["name"] for layout in layouts if layout["key"] == (slide["kind"], slide["chapter"]))
    report_slides.append({"slide": slide["number"], "layout": label, "removed_shapes": len(removal)})

master_part = "ppt/slideMasters/slideMaster1.xml"
master = ET.fromstring(parts[master_part])
common = master.find("p:cSld", NS)
common.insert(0, element('<p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'))
master_tree = common.find("p:spTree", NS)
master_tree.append(rule_shape(TITLE_RULE, 2))
master_tree.append(copied(content_sample["band"], 3, "下の帯"))
master_tree.append(copied(content_sample["credits"][CREDITS[0]], 4, "氏名"))
master_tree.append(copied(content_sample["credits"][CREDITS[1]], 5, "所属"))
master_tree.append(copied(content_sample["page_box"], 6, "番号の箱"))
master_tree.append(number_placeholder(7, xfrm=True, style=True))
footers = master.find("p:hf", NS)
if footers is not None:
    footers.attrib.pop("sldNum", None)

master_rels_part = "ppt/slideMasters/_rels/slideMaster1.xml.rels"
kept = [(item.get("Id"), item.get("Type"), item.get("Target")) for item in ET.fromstring(parts[master_rels_part])
        if item.get("Type") != LAYOUT_TYPE]
layout_ids = master.find("p:sldLayoutIdLst", NS)
for item in list(layout_ids):
    layout_ids.remove(item)
new_rels = list(kept)
for index, layout in enumerate(layouts, 1):
    rel_id = f"rIdLayout{index}"
    new_rels.append((rel_id, LAYOUT_TYPE, f"../slideLayouts/slideLayout{index}.xml"))
    entry = ET.SubElement(layout_ids, q(P, "sldLayoutId"))
    entry.set("id", str(2147483648 + index))
    entry.set(q(R, "id"), rel_id)
    output_parts[f"ppt/slideLayouts/slideLayout{index}.xml"] = layout["xml"]
    output_parts[f"ppt/slideLayouts/_rels/slideLayout{index}.xml.rels"] = relationships(
        [("rId1", MASTER_TYPE, "../slideMasters/slideMaster1.xml")])
output_parts[master_part] = serialize(master)
output_parts[master_rels_part] = relationships(new_rels)

types = ET.fromstring(parts["[Content_Types].xml"])
for item in list(types):
    if item.get("ContentType") == LAYOUT_CONTENT:
        types.remove(item)
for index in range(1, len(layouts) + 1):
    ET.SubElement(types, q(CT, "Override"), PartName=f"/ppt/slideLayouts/slideLayout{index}.xml", ContentType=LAYOUT_CONTENT)
output_parts["[Content_Types].xml"] = serialize(types)

references = set()
merged = {**parts, **output_parts}
for name, content in merged.items():
    if name.endswith(".rels"):
        directory = posixpath.dirname(posixpath.dirname(name))
        for item in ET.fromstring(content):
            if item.get("TargetMode") != "External":
                references.add(posixpath.normpath(posixpath.join(directory, item.get("Target"))))
removed_images = {name for name in removed_images if name not in references}

args.output.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(args.output, "w") as output:
    written = set()
    for entry in entries:
        if entry.filename in removed_images:
            continue
        output.writestr(entry, output_parts.get(entry.filename, parts[entry.filename]))
        written.add(entry.filename)
    for name, content in output_parts.items():
        if name not in written:
            output.writestr(name, content, compress_type=8)

args.report.parent.mkdir(parents=True, exist_ok=True)
args.report.write_text(json.dumps({
    "source": str(args.source), "output": str(args.output),
    "layouts": [layout["name"] for layout in layouts],
    "removed_rule_images": sorted(removed_images), "slides": report_slides,
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"slides": len(slides), "layouts": len(layouts), "removed_rule_images": len(removed_images)}))
