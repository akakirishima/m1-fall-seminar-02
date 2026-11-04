"""Synthetic regression cases for leakage, coverage, times and CSV input."""
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/validate_dataset.py'
spec = importlib.util.spec_from_file_location('validator', SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.rows = {
            'videos': [['V1', 'P1', '10', 'local:synthetic', 'a' * 64]],
            'splits': [['P1', 'pilot', 'synthetic-v1']],
            'coverage': [['V1', 'P1', '0', '10', 'A1', 'synthetic-v1']],
            'labels': [
                ['V1', 'P1', '0', '4', 'absent', 'not_visible', 'A1', 'synthetic-v1', ''],
                ['V1', 'P1', '4', '10', 'present', 'uncertain', 'A1', 'synthetic-v1', ''],
            ],
        }

    def report(self):
        for name, fields in validator.SCHEMAS.items():
            with (self.directory / (name + '.csv')).open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow(fields)
                writer.writerows(self.rows[name])
        return validator.validate(self.directory)

    def fails(self, fragment):
        report = self.report()
        self.assertEqual(report['status'], 'failed')
        self.assertTrue(any(fragment in e['error'] for e in report['errors']), report)

    def test_valid_half_open_boundaries(self):
        self.assertEqual(self.report()['status'], 'passed')

    def test_patient_leakage(self):
        self.rows['splits'].append(['P1', 'test', 'synthetic-v1'])
        self.fails('leakage')

    def test_unlabelled_gap(self):
        self.rows['labels'][1][2] = '5'
        self.fails('exactly cover')

    def test_outside_coverage(self):
        self.rows['coverage'][0][3] = '9'
        self.fails('exactly cover')

    def test_overlapping_labels(self):
        self.rows['labels'][1][2] = '3'
        self.fails('Overlapping')

    def test_wrong_patient(self):
        self.rows['labels'][0][1] = 'P2'
        self.fails('differs')

    def test_nan_and_out_of_range(self):
        for value in ['NaN', 'Infinity', '-1', '11']:
            with self.subTest(value=value):
                self.rows['labels'][1][3] = value
                self.assertEqual(self.report()['status'], 'failed')

    def test_missing_file(self):
        self.report()
        (self.directory / 'splits.csv').unlink()
        self.assertEqual(validator.validate(self.directory)['status'], 'failed')

    def test_empty_templates(self):
        self.rows = {k: [] for k in self.rows}
        self.fails('No data rows')

    def test_bad_label(self):
        self.rows['labels'][0][4] = 'negative'
        self.fails('Unknown adult_hand_arm')

    def test_uncertain_without_reason(self):
        self.rows['labels'][0][4] = 'uncertain'
        self.fails('requires a reason')

    def test_independent_annotators(self):
        self.rows['coverage'].append(['V1', 'P1', '0', '10', 'A2', 'synthetic-v1'])
        self.rows['labels'].append(['V1', 'P1', '0', '10', 'uncertain', 'uncertain', 'A2', 'synthetic-v1', 'synthetic'])
        self.assertEqual(self.report()['status'], 'passed')

    def test_disjoint_coverage(self):
        self.rows['coverage'] = [
            ['V1', 'P1', '0', '4', 'A1', 'synthetic-v1'],
            ['V1', 'P1', '6', '10', 'A1', 'synthetic-v1'],
        ]
        self.rows['labels'][1][2] = '6'
        self.assertEqual(self.report()['status'], 'passed')

    def test_split_version_mixing(self):
        self.rows['videos'].append(['V2', 'P2', '10', 'local:synthetic2', 'b' * 64])
        self.rows['splits'].append(['P2', 'dev', 'synthetic-v2'])
        self.fails('Multiple split versions')

    def test_csv_extra_column(self):
        self.rows['videos'][0].append('unexpected')
        self.fails('Wrong number of columns')


if __name__ == '__main__':
    unittest.main()
