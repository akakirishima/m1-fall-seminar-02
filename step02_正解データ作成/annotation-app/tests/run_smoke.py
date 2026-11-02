"""Browser smoke test with synthetic PNGs. Requires running server and Playwright CLI."""
import argparse
import json
import struct
import subprocess
import zlib
from pathlib import Path

root = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--wrapper', type=Path, default=Path.home()/'.codex/skills/playwright/scripts/playwright_cli.sh')
args = parser.parse_args()
fixture = root/'data/local/annotation-smoke'
fixture.mkdir(parents=True, exist_ok=True)
(root/'output/playwright').mkdir(parents=True, exist_ok=True)
def png(w,h,rgb):
    def chunk(t,d):
        return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+bytes(rgb)*w)*h))+chunk(b'IEND',b'')
for i,c in enumerate([(80,100,90),(125,105,75),(85,95,125)]):
    (fixture/f'frame{i+1}.png').write_bytes(png(640,480,c))
code = Path(__file__).with_name('browser-smoke.js').read_text().replace('PROJECT_ROOT', json.dumps(str(root)))
result = subprocess.run([str(args.wrapper),'-s=annotation','run-code',code],cwd=root,text=True,capture_output=True)
(fixture/'browser-output.txt').write_text(result.stdout+result.stderr)
print(result.stdout)
print(result.stderr)
raise SystemExit(result.returncode)
