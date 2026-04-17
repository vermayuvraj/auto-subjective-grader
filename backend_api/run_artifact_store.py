from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from google.cloud import storage as gcs_storage
except ImportError:  # pragma: no cover - optional until the dependency is installed
    gcs_storage = None


LOGGER = logging.getLogger(__name__)


class RunArtifactStore:
    def __init__(self, bucket_name: Optional[str], prefix: str = "api_runs") -> None:
        self.bucket_name = bucket_name.strip() if bucket_name else None
        self.prefix = prefix.strip().strip("/").replace("\\", "/")
        self._bucket = None
        self._warning_emitted = False

    @property
    def enabled(self) -> bool:
        return bool(self.bucket_name)

    def _warn_unavailable(self) -> None:
        if self._warning_emitted:
            return
        self._warning_emitted = True
        LOGGER.warning(
            "API_RUNS_BUCKET is configured, but google-cloud-storage is not installed. "
            "Durable run storage is disabled until the dependency is available."
        )

    def _get_bucket(self):
        if not self.enabled:
            return None
        if gcs_storage is None:
            self._warn_unavailable()
            return None
        if self._bucket is None:
            client = gcs_storage.Client()
            self._bucket = client.bucket(self.bucket_name)
        return self._bucket

    def _blob_name(self, *parts: str) -> str:
        blob_parts: List[str] = []
        if self.prefix:
            blob_parts.append(self.prefix)
        for part in parts:
            cleaned = str(part).replace("\\", "/").strip("/")
            if cleaned:
                blob_parts.append(cleaned)
        return "/".join(blob_parts)

    def save_json_blob(self, payload: Dict[str, Any], *parts: str) -> bool:
        bucket = self._get_bucket()
        if bucket is None:
            return False
        try:
            bucket.blob(self._blob_name(*parts)).upload_from_string(
                json.dumps(payload, ensure_ascii=False, indent=2),
                content_type="application/json",
            )
            return True
        except Exception:
            LOGGER.exception("Failed to upload JSON blob for %s.", parts)
            return False

    def load_json_blob(self, *parts: str) -> Optional[Dict[str, Any]]:
        bucket = self._get_bucket()
        if bucket is None:
            return None
        try:
            blob = bucket.blob(self._blob_name(*parts))
            if not blob.exists():
                return None
            return json.loads(blob.download_as_bytes().decode("utf-8"))
        except Exception:
            LOGGER.exception("Failed to load JSON blob for %s.", parts)
            return None

    def upload_bytes(self, data: bytes, *parts: str, content_type: str = "application/octet-stream") -> Optional[str]:
        bucket = self._get_bucket()
        if bucket is None:
            return None
        try:
            blob_name = self._blob_name(*parts)
            bucket.blob(blob_name).upload_from_string(data, content_type=content_type)
            return blob_name
        except Exception:
            LOGGER.exception("Failed to upload bytes blob for %s.", parts)
            return None

    def download_blob_to_file(self, destination: Path, *parts: str) -> bool:
        bucket = self._get_bucket()
        if bucket is None:
            return False
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            bucket.blob(self._blob_name(*parts)).download_to_filename(str(destination))
            return True
        except Exception:
            LOGGER.exception("Failed to download blob %s to %s.", parts, destination)
            return False

    def save_run_meta(self, run_id: str, meta: Dict[str, Any]) -> bool:
        return self.save_json_blob(meta, run_id, "run_meta.json")

    def load_run_meta(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self.load_json_blob(run_id, "run_meta.json")

    def list_run_metas(self) -> List[Dict[str, Any]]:
        bucket = self._get_bucket()
        if bucket is None:
            return []
        try:
            prefix = self._blob_name("")
            blob_prefix = f"{prefix}/" if prefix else ""
            metas: List[Dict[str, Any]] = []
            for blob in bucket.list_blobs(prefix=blob_prefix):
                if not blob.name.endswith("/run_meta.json"):
                    continue
                try:
                    metas.append(json.loads(blob.download_as_bytes().decode("utf-8")))
                except Exception:
                    LOGGER.warning("Skipping unreadable run metadata blob: %s", blob.name)
            return metas
        except Exception:
            LOGGER.exception("Failed to list run metadata blobs.")
            return []

    def upload_reports(self, run_id: str, report_dir: Path) -> None:
        bucket = self._get_bucket()
        if bucket is None or not report_dir.exists():
            return
        for report_path in sorted(report_dir.glob("*.pdf")):
            if not report_path.is_file():
                continue
            try:
                bucket.blob(self._blob_name(run_id, "reports", report_path.name)).upload_from_filename(
                    str(report_path),
                    content_type="application/pdf",
                )
            except Exception:
                LOGGER.exception("Failed to upload report %s for run %s.", report_path.name, run_id)

    def load_report_bytes(self, run_id: str, report_name: str) -> Optional[bytes]:
        bucket = self._get_bucket()
        if bucket is None:
            return None
        try:
            blob = bucket.blob(self._blob_name(run_id, "reports", report_name))
            if not blob.exists():
                return None
            return blob.download_as_bytes()
        except Exception:
            LOGGER.exception("Failed to load report %s for run %s.", report_name, run_id)
            return None
