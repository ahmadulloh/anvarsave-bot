import os
from pathlib import Path
from dotenv import load_dotenv

# Initialize static_ffmpeg so ffmpeg is in PATH automatically on Windows/Linux
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "8719226279:AAH3nWRh3-G1a3Gx2drYhhMrRqVH_gDGEag").strip()
BOT_USERNAME = os.getenv("BOT_USERNAME", "anvarsave_bot").replace("@", "").strip()

DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Max file size Telegram Bot API can send (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
