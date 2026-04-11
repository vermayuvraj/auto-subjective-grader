from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from backend_api import main as api_main


class FakeRunArtifactStore:
    def __init__(self) -> None:
        self.enabled = True
        self.metas: dict[str, dict] = {}
        self.reports: dict[tuple[str, str], bytes] = {}

    def save_run_meta(self, run_id: str, meta: dict) -> bool:
        self.metas[run_id] = json.loads(json.dumps(meta))
        return True

    def load_run_meta(self, run_id: str):
        meta = self.metas.get(run_id)
        if meta is None:
            return None
        return json.loads(json.dumps(meta))

    def list_run_metas(self):
        return [json.loads(json.dumps(meta)) for meta in self.metas.values()]

    def upload_reports(self, run_id: str, report_dir: Path) -> None:
        for report_path in report_dir.glob("*.pdf"):
            self.reports[(run_id, report_path.name)] = report_path.read_bytes()

    def load_report_bytes(self, run_id: str, report_name: str):
        return self.reports.get((run_id, report_name))


class ApiRunPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.original_runs_root = api_main.API_RUNS_ROOT
        self.original_store = api_main.RUN_ARTIFACT_STORE
        self.original_cache = dict(api_main.JOB_CACHE)

        api_main.API_RUNS_ROOT = Path(self.tempdir.name)
        api_main.JOB_CACHE.clear()
        self.fake_store = FakeRunArtifactStore()
        api_main.RUN_ARTIFACT_STORE = self.fake_store

    def tearDown(self) -> None:
        api_main.API_RUNS_ROOT = self.original_runs_root
        api_main.RUN_ARTIFACT_STORE = self.original_store
        api_main.JOB_CACHE.clear()
        api_main.JOB_CACHE.update(self.original_cache)
        self.tempdir.cleanup()

    def _build_meta(self, run_id: str, report_dir: str | None = None) -> dict:
        return {
            "run_id": run_id,
            "status": "completed",
            "engine": "SBERT",
            "ocr_backend": "google_vision",
            "student_count": 1,
            "created_at": "2026-04-11T00:00:00Z",
            "started_at": "2026-04-11T00:00:05Z",
            "completed_at": "2026-04-11T00:05:00Z",
            "current_step": 6,
            "total_steps": 6,
            "progress_percent": 100,
            "message": "Evaluation completed successfully.",
            "events": [],
            "elapsed_seconds": 295,
            "eval_dir": None,
            "report_dir": report_dir,
            "summary_rows": [
                {
                    "rank": 1,
                    "student": "Student_1",
                    "total_score": 62.84,
                    "max_score": 100.0,
                    "percentage": 62.84,
                }
            ],
            "reports": [
                {
                    "student": "Student_1",
                    "download_url": f"/api/runs/{run_id}/reports/Student_1_report.pdf",
                }
            ],
            "results": [],
            "error": None,
        }

    def test_load_run_meta_uses_remote_store_when_local_copy_is_missing(self) -> None:
        run_id = "20260411044051-78055838"
        self.fake_store.metas[run_id] = self._build_meta(run_id)

        loaded = api_main._load_run_meta(run_id)

        self.assertEqual(loaded["run_id"], run_id)
        self.assertTrue((Path(self.tempdir.name) / run_id / "run_meta.json").exists())

    def test_list_jobs_includes_remote_run_history(self) -> None:
        run_id = "20260411044051-78055838"
        self.fake_store.metas[run_id] = self._build_meta(run_id)

        jobs = api_main.list_jobs()

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["run_id"], run_id)
        self.assertEqual(jobs[0]["top_student"], "Student_1")

    def test_download_report_falls_back_to_remote_storage(self) -> None:
        run_id = "20260411044051-78055838"
        report_name = "Student_1_report.pdf"
        report_dir = str(Path(self.tempdir.name) / run_id / "outputs" / "reports")
        self.fake_store.metas[run_id] = self._build_meta(run_id, report_dir=report_dir)
        self.fake_store.reports[(run_id, report_name)] = b"%PDF-1.4 remote-report"

        response = api_main.download_report(run_id, report_name)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"%PDF-1.4 remote-report")
        self.assertEqual(response.media_type, "application/pdf")


if __name__ == "__main__":
    unittest.main()
