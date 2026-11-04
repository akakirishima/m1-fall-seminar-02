"""Exercise record validation with synthetic, temporary files only."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import ai_records


class RecordChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ai-record-check-")
        self.root = Path(self.temporary.name)
        for step in ("step01", "step02", "step03", "step04"):
            directory = self.root / step
            directory.mkdir()
            (directory / "README.md").write_text("synthetic fixture", encoding="utf-8")
        self.run = self.root / "step01/runs/synthetic_001"
        (self.run / "code_snapshot").mkdir(parents=True)
        script = self.run / "code_snapshot/example.py"
        script.write_text("print('synthetic fixture')\n", encoding="utf-8")
        self.artifact = self.root / "synthetic.txt"
        self.artifact.write_text("synthetic fixture\n", encoding="utf-8")
        self.record = ai_records.read_json(ai_records.ROOT / "templates/experiment_manifest.json")
        self.record.update({
            "is_template": False, "run_id": "synthetic_001", "step_id": "step01",
            "operation": "synthetic_record_test", "purpose": "test record checks, not a model",
            "status": "completed", "plan_version": "test", "started_at": "2026-10-30T00:00:00+09:00",
            "finished_at": "2026-10-30T00:00:01+09:00", "command_argv": ["python", "example.py"],
            "working_directory": ".", "code": [{"id": "script", "snapshot_ref": "code_snapshot/example.py", "sha256": hashlib.sha256(script.read_bytes()).hexdigest()}],
            "config": {"synthetic": True}, "environment": {"synthetic": True},
            "exit_code": 0, "validation": {"status": "passed", "checks": []},
        })
        artifact = {"id": "synthetic", "role": "test_fixture", "version": "v1",
                    "sha256": hashlib.sha256(self.artifact.read_bytes()).hexdigest(),
                    "storage": "repository", "ref": "synthetic.txt"}
        self.record["inputs"] = [dict(artifact)]
        self.record["outputs"] = [dict(artifact)]
        state = {"schema_version": 1, "current_step": "step01", "documents": {},
                 "steps": [{"id": key, "readme": key + "/README.md"} for key in sorted(ai_records.STEPS)]}
        ai_records.write_json(self.root / "research_state.json", state)

    def tearDown(self):
        self.temporary.cleanup()

    def save(self):
        ai_records.write_json(self.run / "manifest.json", self.record)
        ai_records.write_json(self.root / "experiment_index.json", ai_records.build_index(self.root))

    def test_complete_record_and_saved_files(self):
        self.save()
        self.assertEqual(ai_records.check(self.root)["errors"], [])

    def test_template_cannot_be_an_experiment(self):
        template = ai_records.read_json(ai_records.ROOT / "templates/experiment_manifest.json")
        self.assertIn("template is not an experiment", ai_records.validate_manifest(template))

    def test_completed_record_cannot_omit_inputs(self):
        self.record["inputs"] = []
        self.assertTrue(ai_records.validate_manifest(self.record))

    def test_failed_run_requires_reason(self):
        self.record.update(status="failed", exit_code=1)
        self.assertTrue(ai_records.validate_manifest(self.record))
        self.record["failure"] = {"type": "synthetic", "message": "expected test failure"}
        self.assertEqual(ai_records.validate_manifest(self.record), [])

    def test_changed_input_is_detected(self):
        self.save()
        self.artifact.write_text("changed synthetic fixture", encoding="utf-8")
        self.assertTrue(any("changed artifact" in e for e in ai_records.check(self.root)["errors"]))

    def test_changed_code_is_detected(self):
        self.save()
        (self.run / "code_snapshot/example.py").write_text("changed", encoding="utf-8")
        self.assertTrue(any("code snapshot" in e for e in ai_records.check(self.root)["errors"]))

    def test_missing_parent_and_cycle_are_detected(self):
        self.record["parent_run_ids"] = ["missing_parent"]
        self.save()
        self.assertTrue(any("unknown parent" in e for e in ai_records.check(self.root)["errors"]))
        self.record["parent_run_ids"] = ["synthetic_001"]
        self.save()
        self.assertTrue(any("cyclic" in e for e in ai_records.check(self.root)["errors"]))

    def test_local_paths_do_not_enter_shared_artifact_record(self):
        self.record["inputs"][0].update(storage="local_only", ref="patient/local/path")
        self.assertTrue(any("local-only" in e for e in ai_records.validate_manifest(self.record)))

    def test_stale_index_is_detected(self):
        self.save()
        self.record["purpose"] = "changed purpose"
        self.record["status"] = "failed"
        self.record["failure"] = "synthetic failure"
        ai_records.write_json(self.run / "manifest.json", self.record)
        self.assertTrue(any("stale" in e for e in ai_records.check(self.root)["errors"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
