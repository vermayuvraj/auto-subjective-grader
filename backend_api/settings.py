import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3100",
    "http://127.0.0.1:3100",
]


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


@dataclass(frozen=True)
class AppSettings:
    poppler_path: Optional[str]
    api_runs_root: Path
    readme_path: Path
    allowed_origins: List[str]
    easyocr_use_gpu: bool
    azure_endpoint: Optional[str]
    azure_key: Optional[str]
    gemini_api_key_present: bool


def load_settings(project_root: Path) -> AppSettings:
    poppler_path = os.getenv("POPPLER_PATH")
    api_runs_root = Path(os.getenv("API_RUNS_ROOT", str(project_root / "results" / "api_runs")))
    readme_path = Path(os.getenv("README_PATH", str(project_root / "README.md")))
    allowed_origins = _read_csv("ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS)

    azure_endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    azure_key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    return AppSettings(
        poppler_path=poppler_path,
        api_runs_root=api_runs_root,
        readme_path=readme_path,
        allowed_origins=allowed_origins,
        easyocr_use_gpu=_read_bool("EASYOCR_USE_GPU", False),
        azure_endpoint=azure_endpoint,
        azure_key=azure_key,
        gemini_api_key_present=bool(gemini_api_key),
    )
