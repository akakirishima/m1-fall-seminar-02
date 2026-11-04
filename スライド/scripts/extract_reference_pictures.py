"""Copy pictures and chart values from reference PPTX slides into the Web slide assets.

The source PPTX is opened read-only. Picture positions are converted to the
1200px-wide Slidev canvas so that components can place them like the source.
"""
import argparse
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
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "asvg": "http://schemas.microsoft.com/office/drawing/2016/SVG/main",
}
R_ID = f"{{{NS['r']}}}id"
R_EMBED = f"{{{NS['r']}}}embed"


def rels(archive, member):
    path = posixpath.join(posixpath.dirname(member), "_rels", posixpath.basename(member) + ".rels")
    root = ET.fromstring(archive.read(path))
    return {item.attrib["Id"]: posixpath.normpath(posixpath.join(posixpath.dirname(member), item.attrib["Target"]))
            for item in root}


def chart_values(archive, member):
    root = ET.fromstring(archive.read(member))
    series = []
    for ser in root.iter(f"{{{NS['c']}}}ser"):
        name = "".join(v.text or "" for v in ser.findall("c:tx//c:v", NS))
        cats = [v.text for v in ser.findall("c:cat//c:pt/c:v", NS)]
        vals = [float(v.text) for v in ser.findall("c:val//c:pt/c:v", NS)]
        series.append({"name": name, "categories": cats, "values": vals})
    return series


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("asset_dir", type=Path)
    parser.add_argument("record", type=Path)
    parser.add_argument("--slides", type=int, nargs="+", required=True)
    args = parser.parse_args()
    args.asset_dir.mkdir(parents=True, exist_ok=True)
    result = {"source": str(args.source), "slides": {}}
    with ZipFile(args.source) as archive:
        presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
        scale = 1200 / int(presentation.find("p:sldSz", NS).attrib["cx"])
        targets = rels(archive, "ppt/presentation.xml")
        order = [targets[item.attrib[R_ID]] for item in presentation.findall("p:sldIdLst/p:sldId", NS)]
        for number in args.slides:
            member = order[number - 1]
            links = rels(archive, member)
            root = ET.fromstring(archive.read(member))
            pictures, charts = [], []
            for index, pic in enumerate(root.iter(f"{{{NS['p']}}}pic"), 1):
                blip = pic.find(".//a:blip", NS)
                svg = blip.find(".//asvg:svgBlip", NS)
                target = links[(svg if svg is not None else blip).attrib[R_EMBED if svg is None else R_EMBED]]
                xfrm = pic.find("p:spPr/a:xfrm", NS)
                off, ext = xfrm.find("a:off", NS).attrib, xfrm.find("a:ext", NS).attrib
                src = pic.find("p:blipFill/a:srcRect", NS)
                name = f"slide-{number:03d}-picture-{index:02d}{Path(target).suffix}"
                (args.asset_dir / name).write_bytes(archive.read(target))
                pictures.append({
                    "file": name, "source_member": target,
                    "name": pic.find("p:nvPicPr/p:cNvPr", NS).attrib.get("name"),
                    "x": round(int(off["x"]) * scale, 3), "y": round(int(off["y"]) * scale, 3),
                    "w": round(int(ext["cx"]) * scale, 3), "h": round(int(ext["cy"]) * scale, 3),
                    "crop": [int(src.attrib.get(k, 0)) for k in ("l", "t", "r", "b")] if src is not None and src.attrib else None,
                    "rotation": int(xfrm.attrib.get("rot", 0)) / 60000,
                    "flipH": xfrm.attrib.get("flipH") == "1",
                })
            for frame in root.iter(f"{{{NS['p']}}}graphicFrame"):
                chart = frame.find(".//c:chart", NS)
                if chart is not None:
                    charts.append(chart_values(archive, links[chart.attrib[R_ID]]))
            result["slides"][number] = {"member": member, "pictures": pictures, "charts": charts}
    args.record.parent.mkdir(parents=True, exist_ok=True)
    args.record.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()


def crop_presented_ellipse(page_image: Path, box, output: Path):
    """Cut an elliptical photo out of a rendered page of the presented PDF.

    Used where the presented version already carries the face cover, so the
    cover stays exactly as it was shown.
    """
    from PIL import Image, ImageDraw
    image = Image.open(page_image).convert("RGB").crop(box)
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, image.size[0] - 1, image.size[1] - 1), fill=255)
    image.putalpha(mask)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
