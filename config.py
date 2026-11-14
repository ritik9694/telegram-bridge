import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def get_required(name):
    value = os.getenv(name, "").strip()
    if not value or value.startswith("YOUR_"):
        raise ValueError(f"Missing configuration: {name}")
    return value


API_ID = int(get_required("API_ID"))
API_HASH = get_required("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "xenovra_session")

SOURCE_CHAT_ID = os.getenv("SOURCE_CHAT_ID", "").strip()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
BOT_USERNAME = os.getenv("BOT_USERNAME", "").strip()

XENOVRA_URL = os.getenv(
    "XENOVRA_URL", "http://localhost:8000"
).rstrip("/")
XENOVRA_EMAIL = os.getenv("XENOVRA_EMAIL", "").strip()
XENOVRA_PASSWORD = os.getenv("XENOVRA_PASSWORD", "").strip()
STORAGE_ID = os.getenv("STORAGE_ID", "").strip()

DOWNLOAD_DIR = BASE_DIR / os.getenv("DOWNLOAD_DIR", "downloads")
MAX_CONCURRENT_DOWNLOADS = int(
    os.getenv("MAX_CONCURRENT_DOWNLOADS", "1")
)

DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
NOTIFY_CHAT_ID = os.getenv("NOTIFY_CHAT_ID", "").strip()
PUBLIC_VIDEO_CHANNEL = os.getenv("PUBLIC_VIDEO_CHANNEL", "").strip()
