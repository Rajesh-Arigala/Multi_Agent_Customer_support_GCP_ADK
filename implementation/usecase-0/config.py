import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))

APP_ENV = os.getenv("APP_ENV", "development")
PORT = int(os.getenv("PORT", "5000"))

