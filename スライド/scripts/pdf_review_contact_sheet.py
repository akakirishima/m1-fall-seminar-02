"""Arrange existing PDF page renders into contact sheets for source review."""
import argparse
from pathlib import Path
from PIL import Image, ImageOps

parser = argparse.ArgumentParser()
parser.add_argument("directory", type=Path)
parser.add_argument("--prefix", default="page-")
args = parser.parse_args()
pages = sorted(args.directory.glob(f"{args.prefix}*.png"))
for start in range(0, len(pages), 6):
    canvas = Image.new("RGB", (1220, 1410), "#cccccc")
    for index, path in enumerate(pages[start:start + 6]):
        with Image.open(path) as original:
            thumb = ImageOps.contain(original.convert("RGB"), (600, 460))
            canvas.paste(thumb, (10 + (index % 2) * 610, 10 + (index // 2) * 465))
    output = args.directory / f"contact-{start // 6 + 1:02d}.png"
    canvas.save(output)
    print(output)
