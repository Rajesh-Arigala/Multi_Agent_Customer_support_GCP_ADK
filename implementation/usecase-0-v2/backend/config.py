import os
from pathlib import Path

from backend.storage.schema import DEFAULT_SHEET_TABS


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "multi-agent-adk-1")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING_BUCKET = os.getenv("STAGING_BUCKET", "gs://multi-agent-adk-1-adk-agent")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "1zwyHaspgLVjE5Xax0c9riylI6CBirf12v98k6mgp2c8")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))

SHEET_TABS = DEFAULT_SHEET_TABS


BACKEND_SERVICE_ACCOUNT = os.getenv("BACKEND_SERVICE_ACCOUNT", "multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com")

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-005")
