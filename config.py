import os
from pathlib import Path
from dotenv import load_dotenv

# Initialize static_ffmpeg so ffmpeg and ffprobe are in PATH automatically on Windows/Linux
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Support 3 bot tokens (with fallback to BOT_TOKEN for 1st bot)
BOT_TOKEN_1 = os.getenv("BOT_TOKEN_1", os.getenv("BOT_TOKEN", "8719226279:AAH3nWRh3-G1a3Gx2drYhhMrRqVH_gDGEag")).strip()
BOT_TOKEN_2 = os.getenv("BOT_TOKEN_2", "").strip()
BOT_TOKEN_3 = os.getenv("BOT_TOKEN_3", "").strip()

# Collect all configured tokens in order
BOT_TOKENS = [t for t in [BOT_TOKEN_1, BOT_TOKEN_2, BOT_TOKEN_3] if t]

BOT_USERNAME = os.getenv("BOT_USERNAME", "anvarsave_bot").replace("@", "").strip()

DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Max file size Telegram Bot API can send directly (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# YouTube Cookies handling (bypasses Render/Cloud datacenter blocks)
YOUTUBE_COOKIES = os.getenv("YOUTUBE_COOKIES", "").strip()
LOCAL_COOKIES = BASE_DIR / "cookies.txt"
RENDER_SECRET_COOKIES = Path("/etc/secrets/cookies.txt")

COOKIES_PATH: Path | None = None
if RENDER_SECRET_COOKIES.exists():
    COOKIES_PATH = RENDER_SECRET_COOKIES
elif LOCAL_COOKIES.exists():
    COOKIES_PATH = LOCAL_COOKIES
elif YOUTUBE_COOKIES:
    try:
        LOCAL_COOKIES.write_text(YOUTUBE_COOKIES, encoding="utf-8")
        COOKIES_PATH = LOCAL_COOKIES
    except Exception:
        COOKIES_PATH = None
