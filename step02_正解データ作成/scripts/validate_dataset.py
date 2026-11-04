"""Validate CSV structure, patient splits, and fully labelled coverage; no media access."""
import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

SCHEMAS = {
    'videos': ['video_id', 'patient_id', 'duration_s', 'source_ref', 'sha256'],
    'splits': ['patient_id', 'split', 'split_version'],
    'coverage': ['video_id', 'patient_id', 'start_s', 'end_s', 'annotator', 'annotation_version'],
    'labels': ['video_id', 'patient_id', 'start_s', 'end_s', 'adult_hand_arm',
               'contact_evidence', 'annotator', 'annotation_version', 'note'],
}


def validate(directory):
    errors, tables, hashes = [], {}, {}
    def error(file, row, message):
        errors.append({'file': file, 'row': row, 'error': message})
    for name, fields in SCHEMAS.items():
        path = directory / (name + '.csv')
        tables[name] = []
        try:
            hashes[name + '.csv'] = hashlib.sha256(path.read_bytes()).hexdigest()
            with path.open(encoding='utf-8-sig', newline='') as stream:
                reader = csv.DictReader(stream)
                if reader.fieldnames != fields:
                    error(name, 1, 'Header must be exactly: ' + ','.join(fields))
                    continue
                for line, row in enumerate(reader, 2):
                    if None in row or any(v is None for v in row.values()):
                        error(name, line, 'Wrong number of columns')
                        continue
                    row = {k: v.strip() for k, v in row.items()}
                    missing = [k for k, v in row.items() if not v and k != 'note']
                    if missing:
                        error(name, line, 'Empty required fields: ' + ', '.join(missing))
                        continue
                    tables[name].append((line, row))
                if not tables[name]:
                    error(name, 1, 'No data rows; a blank template is not a dataset')
        except (OSError, UnicodeError, csv.Error) as exc:
            error(name, None, str(exc))

    def number(value, file, line):
        try:
            result = Decimal(value)
            if not result.is_finite():
                raise InvalidOperation
            return result
        except InvalidOperation:
            error(file, line, 'Time must be a finite decimal number: ' + value)
            return None

    videos = {}
    for line, row in tables['videos']:
        vid = row['video_id']
        if vid in videos:
            error('videos', line, 'Duplicate video_id: ' + vid)
        duration = number(row['duration_s'], 'videos', line)
        if duration is not None and duration <= 0:
            error('videos', line, 'duration_s must be positive')
        if not re.fullmatch(r'[a-fA-F0-9]{64}', row['sha256']):
            error('videos', line, 'sha256 must contain 64 hexadecimal characters')
        videos[vid] = (row['patient_id'], duration)

    splits, versions = {}, set()
    for line, row in tables['splits']:
        patient = row['patient_id']
        if patient in splits:
            error('splits', line, 'Duplicate patient or patient leakage: ' + patient)
        if row['split'] not in {'pilot', 'train', 'dev', 'test'}:
            error('splits', line, 'Unknown split: ' + row['split'])
        splits[patient] = row['split']
        versions.add(row['split_version'])
    if len(versions) > 1:
        error('splits', None, 'Multiple split versions in one manifest')
    patients = {p for p, _ in videos.values()}
    for patient in sorted(patients - splits.keys()):
        error('splits', None, 'Missing split for patient: ' + patient)
    for patient in sorted(splits.keys() - patients):
        error('splits', None, 'Patient has no registered video: ' + patient)

    groups = {'coverage': defaultdict(list), 'labels': defaultdict(list)}
    for name in groups:
        for line, row in tables[name]:
            vid = row['video_id']
            if vid not in videos:
                error(name, line, 'Unknown video_id: ' + vid)
                continue
            patient, duration = videos[vid]
            if row['patient_id'] != patient:
                error(name, line, 'patient_id differs from videos.csv')
            start = number(row['start_s'], name, line)
            end = number(row['end_s'], name, line)
            if start is None or end is None or duration is None:
                continue
            if not (0 <= start < end <= duration):
                error(name, line, 'Require 0 <= start_s < end_s <= duration_s')
                continue
            if name == 'labels':
                if row['adult_hand_arm'] not in {'present', 'absent', 'uncertain'}:
                    error(name, line, 'Unknown adult_hand_arm label')
                if row['contact_evidence'] not in {'visible', 'not_visible', 'uncertain'}:
                    error(name, line, 'Unknown contact_evidence label')
                if row['adult_hand_arm'] == 'uncertain' and not row['note']:
                    error(name, line, 'uncertain requires a reason in note')
            key = (vid, row['annotator'], row['annotation_version'])
            groups[name][key].append((start, end, line))

    for name, mapping in groups.items():
        for key, spans in mapping.items():
            spans.sort()
            furthest_end = Decimal('-1')
            for start, end, line in spans:
                if start < furthest_end:
                    error(name, line, 'Overlapping intervals for ' + str(key))
                furthest_end = max(furthest_end, end)

    def union(spans):
        merged = []
        for start, end, _ in sorted(spans):
            if merged and start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
            else:
                merged.append((start, end))
        return merged

    for key in groups['coverage'].keys() | groups['labels'].keys():
        coverage = groups['coverage'].get(key, [])
        labels = groups['labels'].get(key, [])
        if union(coverage) != union(labels):
            error('labels', None, 'Labels must exactly cover registered coverage, with no extra time: ' + str(key))

    return {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'scope': 'CSV consistency only; no media, label correctness, historical leakage, or sample-size validation',
        'status': 'passed' if not errors else 'failed',
        'input_sha256': hashes,
        'rows': {k: len(v) for k, v in tables.items()},
        'patients': len(patients),
        'split_counts': {s: sum(x == s for x in splits.values()) for s in ['pilot', 'train', 'dev', 'test']},
        'errors': errors,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output exists; choose a new run path')
    report = validate(args.input_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'status': report['status'], 'rows': report['rows'], 'errors': len(report['errors'])}))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
