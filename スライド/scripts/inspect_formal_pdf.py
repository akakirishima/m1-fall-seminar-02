"""Read the formal presentation PDF and optionally render selected pages."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from pypdf import PdfReader


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--render-pages", type=int, nargs="*", default=[])
    parser.add_argument("--pdftoppm", type=Path)
    args = parser.parse_args()
    reader = PdfReader(args.source)
    pages = [{"number": number, "text": page.extract_text() or "",
              "width_pt": float(page.mediabox.width), "height_pt": float(page.mediabox.height)}
             for number, page in enumerate(reader.pages, 1)]
    for number in (1, 7, 15, 18, 47, 48):
        if number > len(reader.pages):
            continue
        spans = []
        def visit(text, current_matrix, text_matrix, font, font_size):
            if text.strip():
                spans.append({"text": text.strip(), "font_size_pt": font_size,
                              "text_matrix": text_matrix, "current_matrix": current_matrix})
        reader.pages[number - 1].extract_text(visitor_text=visit)
        pages[number - 1]["spans"] = spans
    digest = hashlib.sha256(args.source.read_bytes()).hexdigest()
    result = {"source": str(args.source), "sha256": digest, "page_count": len(pages), "pages": pages}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"page_count": len(pages), "sha256": digest}, ensure_ascii=False))
    for page in pages:
        lines = [line.strip() for line in page["text"].splitlines() if line.strip()]
        print(f"{page['number']:02d}: {' / '.join(lines[:2])[:160]}")
    for number in args.render_pages:
        prefix = args.output.parent / f"formal-{number:03d}"
        subprocess.run([str(args.pdftoppm), "-f", str(number), "-l", str(number),
                        "-scale-to-x", "1200", "-scale-to-y", "900", "-singlefile", "-png",
                        str(args.source), str(prefix)], check=True)
        print(f"Rendered {number}")
