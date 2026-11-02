"""Record primary full-text metadata and selected methods without model execution."""
import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

URL = 'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11644908/fullTextXML'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error('Choose a new output directory')
    args.output_dir.mkdir(parents=True)
    snapshot = args.output_dir / 'code_snapshot'
    snapshot.mkdir()
    shutil.copyfile(__file__, snapshot / Path(__file__).name)
    report = {'retrieved_at': datetime.now(timezone.utc).isoformat(), 'url': URL,
              'command': sys.argv, 'status': 'failed'}
    try:
        with urlopen(Request(URL, headers={'User-Agent': 'infant-intervention-literature-check'}), timeout=30) as response:
            data = response.read()
        root = ET.fromstring(data)
        def content(el):
            return ' '.join(' '.join(el.itertext()).split()) if el is not None else None
        report.update({
            'status': 'success', 'source_sha256': hashlib.sha256(data).hexdigest(),
            'title': content(root.find('.//article-title')),
            'ids': {e.get('pub-id-type'): e.text for e in root.findall('.//article-meta/article-id')},
            'authors': [{'surname': content(e.find('name/surname')), 'given_names': content(e.find('name/given-names'))}
                        for e in root.findall('.//article-meta/contrib-group/contrib') if e.get('contrib-type') == 'author'],
            'sections': [{'title': content(sec.find('title')), 'paragraphs': [content(p) for p in sec.findall('p')]}
                         for sec in root.findall('.//body//sec')
                         if (content(sec.find('title')) or '').startswith(('2.1.1.', '2.2.', '2.3.'))],
            'related_references': [content(e) for e in root.findall('.//ref-list/ref')
                                   if 'RGB-D Scene Analysis' in content(e)],
            'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        })
    except Exception as exc:
        report['error'] = f'{type(exc).__name__}: {exc}'
    (args.output_dir / 'source_check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'success' else 1


if __name__ == '__main__':
    raise SystemExit(main())
