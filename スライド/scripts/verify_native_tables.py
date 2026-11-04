"""Verify exported native PowerPoint tables against the captured Web cell contents."""
import argparse
import json
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
parser = argparse.ArgumentParser()
parser.add_argument("pptx", type=Path)
parser.add_argument("table_data", type=Path)
parser.add_argument("report", type=Path)
args = parser.parse_args()
expected = json.loads(args.table_data.read_text(encoding="utf-8-sig"))
errors = []
records = []
normalize = lambda text: "".join(text.split())
with ZipFile(args.pptx) as archive:
    for slide in expected["slides"]:
        root = ET.fromstring(archive.read(f"ppt/slides/slide{slide['number']}.xml"))
        tables = root.findall(".//a:tbl", NS)
        if len(tables) != len(slide["tables"]):
            errors.append(f"Slide {slide['number']}: native table count mismatch")
        for table, spec in zip(tables, slide["tables"]):
            rows = table.findall("a:tr", NS)
            if len(rows) != len(spec["rows"]):
                errors.append(f"Slide {slide['number']}: row count mismatch")
            for r, (row, row_spec) in enumerate(zip(rows, spec["rows"]), 1):
                cells = row.findall("a:tc", NS)
                if len(cells) != len(row_spec["cells"]):
                    errors.append(f"Slide {slide['number']}: column count mismatch in row {r}")
                for c, (cell, cell_spec) in enumerate(zip(cells, row_spec["cells"]), 1):
                    actual = "".join(node.text or "" for node in cell.findall(".//a:t", NS))
                    if normalize(actual) != normalize(cell_spec["text"]):
                        errors.append(f"Slide {slide['number']}: cell ({r},{c}) text mismatch")
            records.append({"slide": slide["number"], "rows": len(rows),
                            "columns": len(table.findall("a:tblGrid/a:gridCol", NS))})
    total = sum(len(ET.fromstring(archive.read(name)).findall(".//a:tbl", NS))
                for name in archive.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml"))
    if total != len(records):
        errors.append("Unexpected native tables outside captured pages")
report = {"native_tables": total, "tables": records, "errors": errors,
          "scope": "PowerPoint native table XML, row/column counts, all cell text"}
args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"native_tables": total, "errors": errors}))
raise SystemExit(bool(errors))
