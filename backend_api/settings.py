import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import google.auth


DEFAULT_ALLOWED_ORIGINS = ["*"]


def _read_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _read_csv(name: str, default: List[str]) -> List[str]:
    raw = os.getenv(name)
    if not raw:
        return default
    items = [item.strip() for item in raw.split(",")]
    return [item for item in items if item]


def _default_adc_path() -> Optional[str]:
    if os.name == "nt":
        appdata = os.getenv("APPDATA")
        if not appdata:
            return None
        return str(Path(appdata) / "gcloud" / "application_default_credentials.json")

    return str(Path.home() / ".config" / "gcloud" / "application_default_credentials.json")


def _should_attempt_adc_project_resolution() -> bool:
    explicit_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if explicit_credentials:
        return Path(explicit_credentials).exists()

    adc_path = _default_adc_path()
    if adc_path and Path(adc_path).exists():
        return True

    return bool(
        os.getenv("K_SERVICE")
        or os.getenv("FUNCTION_TARGET")
        or os.getenv("GAE_ENV")
    )


@dataclass(frozen=True)
class AppSettings:
    poppler_path: Optional[str]
    api_runs_root: Path
    api_runs_bucket: Optional[str]
    api_runs_prefix: str
    readme_path: Path
    allowed_origins: List[str]
    easyocr_use_gpu: bool
    google_vision_language_hints: List[str]
    azure_endpoint: Optional[str]
    azure_key: Optional[str]
    vertex_ai_project: Optional[str]
    vertex_ai_location: str
    gemini_configured: bool


def _resolve_vertex_ai_project() -> Optional[str]:
    for name in ("VERTEX_AI_PROJECT", "GOOGLE_CLOUD_PROJECT", "GCLOUD_PROJECT", "GCP_PROJECT"):
        raw = os.getenv(name)
        if raw:
            return raw.strip()

    if not _should_attempt_adc_project_resolution():
        return None

    try:
        _, project_id = google.auth.default()
    except Exception:
        return None

    return project_id.strip() if project_id else None


def load_settings(project_root: Path) -> AppSettings:
    poppler_path = os.getenv("POPPLER_PATH")
    api_runs_root = Path(os.getenv("API_RUNS_ROOT", str(project_root / "results" / "api_runs")))
    api_runs_bucket = os.getenv("API_RUNS_BUCKET")
    api_runs_prefix = os.getenv("API_RUNS_PREFIX", "api_runs")
    readme_path = Path(os.getenv("README_PATH", str(project_root / "README.md")))
    allowed_origins = _read_csv("ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS)
    google_vision_language_hints = _read_csv(
        "GOOGLE_VISION_LANGUAGE_HINTS",
        ["en-t-i0-handwrit", "en"],
    )

    azure_endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    azure_key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    vertex_ai_project = _resolve_vertex_ai_project()
    vertex_ai_location = (
        os.getenv("VERTEX_AI_LOCATION")
        or os.getenv("GOOGLE_CLOUD_LOCATION")
        or "global"
    )

    return AppSettings(
        poppler_path=poppler_path,
        api_runs_root=api_runs_root,
        api_runs_bucket=api_runs_bucket,
        api_runs_prefix=api_runs_prefix,
        readme_path=readme_path,
        allowed_origins=allowed_origins,
        easyocr_use_gpu=_read_bool("EASYOCR_USE_GPU", False),
        google_vision_language_hints=google_vision_language_hints,
        azure_endpoint=azure_endpoint,
        azure_key=azure_key,
        vertex_ai_project=vertex_ai_project,
        vertex_ai_location=vertex_ai_location,
        gemini_configured=bool(vertex_ai_project),
    )
