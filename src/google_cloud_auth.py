from __future__ import annotations

import datetime as _dt
import os
import shutil
import subprocess
import threading
from typing import Optional

try:
    import google.auth
    from google.auth import credentials as google_auth_credentials
    from google.auth.exceptions import DefaultCredentialsError, RefreshError
except ImportError:  # optional until Google-backed features are used
    google = None  # type: ignore[assignment]
    google_auth_credentials = None  # type: ignore[assignment]
    DefaultCredentialsError = Exception  # type: ignore[assignment]
    RefreshError = Exception  # type: ignore[assignment]


_GCLOUD_LOCK = threading.Lock()
_GCLOUD_ACCESS_TOKEN: Optional[str] = None
_GCLOUD_TOKEN_EXPIRES_AT: Optional[_dt.datetime] = None
_GCLOUD_PROJECT_ID: Optional[str] = None
_CLOUD_PLATFORM_SCOPE = "https://www.googleapis.com/auth/cloud-platform"


def _utcnow_naive() -> _dt.datetime:
    return _dt.datetime.utcnow()


def _gcloud_executable() -> Optional[str]:
    return shutil.which("gcloud")


def _run_gcloud(*args: str) -> Optional[str]:
    exe = _gcloud_executable()
    if not exe:
        return None

    try:
        completed = subprocess.run(
            [exe, *args],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except Exception:
        return None

    output = (completed.stdout or "").strip()
    return output or None


def _default_adc_path() -> Optional[str]:
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            return None
        return os.path.join(appdata, "gcloud", "application_default_credentials.json")

    return os.path.join(os.path.expanduser("~"), ".config", "gcloud", "application_default_credentials.json")


def has_adc_credentials() -> bool:
    explicit_credentials = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if explicit_credentials and os.path.exists(explicit_credentials):
        return True

    adc_path = _default_adc_path()
    return bool(adc_path and os.path.exists(adc_path))


def running_on_google_cloud() -> bool:
    return bool(
        os.environ.get("K_SERVICE")
        or os.environ.get("FUNCTION_TARGET")
        or os.environ.get("GAE_ENV")
    )


def resolve_google_cloud_project_id() -> Optional[str]:
    global _GCLOUD_PROJECT_ID

    for env_name in ("VERTEX_AI_PROJECT", "GOOGLE_CLOUD_PROJECT", "GCLOUD_PROJECT", "GCP_PROJECT"):
        value = os.environ.get(env_name)
        if value and value.strip():
            return value.strip()

    if google is not None and (has_adc_credentials() or running_on_google_cloud()):
        try:
            _, project_id = google.auth.default(scopes=[_CLOUD_PLATFORM_SCOPE])
        except Exception:
            project_id = None
        if project_id:
            return project_id.strip()

    with _GCLOUD_LOCK:
        if _GCLOUD_PROJECT_ID:
            return _GCLOUD_PROJECT_ID

    project_id = _run_gcloud("config", "get-value", "project")
    if not project_id or project_id == "(unset)":
        return None

    project_id = project_id.strip()
    with _GCLOUD_LOCK:
        _GCLOUD_PROJECT_ID = project_id
    return project_id


def get_gcloud_access_token(force_refresh: bool = False) -> Optional[str]:
    global _GCLOUD_ACCESS_TOKEN, _GCLOUD_TOKEN_EXPIRES_AT

    with _GCLOUD_LOCK:
        now = _utcnow_naive()
        if (
            not force_refresh
            and _GCLOUD_ACCESS_TOKEN
            and _GCLOUD_TOKEN_EXPIRES_AT
            and _GCLOUD_TOKEN_EXPIRES_AT > now + _dt.timedelta(minutes=2)
        ):
            return _GCLOUD_ACCESS_TOKEN

    token = _run_gcloud("auth", "print-access-token")
    if not token:
        return None

    expiry = _utcnow_naive() + _dt.timedelta(minutes=45)
    with _GCLOUD_LOCK:
        _GCLOUD_ACCESS_TOKEN = token
        _GCLOUD_TOKEN_EXPIRES_AT = expiry
    return token


class GcloudAccessTokenCredentials(google_auth_credentials.Credentials):  # type: ignore[misc]
    def __init__(self, quota_project_id: Optional[str] = None):
        super().__init__()
        self.token: Optional[str] = None
        self.expiry: Optional[_dt.datetime] = None
        self._quota_project_id = quota_project_id

    @property
    def quota_project_id(self) -> Optional[str]:
        return self._quota_project_id

    def refresh(self, request) -> None:  # pragma: no cover - exercised via clients
        token = get_gcloud_access_token(force_refresh=True)
        if not token:
            raise RefreshError(
                "Unable to acquire a Google Cloud access token from gcloud. "
                "Run `gcloud auth login` and ensure a project is selected."
            )
        self.token = token
        self.expiry = _utcnow_naive() + _dt.timedelta(minutes=45)


def get_google_auth_credentials():
    if google is None:
        raise RuntimeError(
            "google-auth is not installed. Install Google client libraries before using Vertex AI or Google Vision."
        )

    if has_adc_credentials() or running_on_google_cloud():
        try:
            credentials, _ = google.auth.default(scopes=[_CLOUD_PLATFORM_SCOPE])
            return credentials
        except DefaultCredentialsError:
            pass
        except Exception:
            pass

    project_id = resolve_google_cloud_project_id()
    token = get_gcloud_access_token()
    if token:
        credentials = GcloudAccessTokenCredentials(quota_project_id=project_id)
        credentials.token = token
        credentials.expiry = _utcnow_naive() + _dt.timedelta(minutes=45)
        return credentials

    raise RuntimeError(
        "Google Cloud credentials are not available. Either run "
        "`gcloud auth application-default login`, or sign in with `gcloud auth login` "
        "and select a project so the local fallback can use your existing Cloud session."
    )
