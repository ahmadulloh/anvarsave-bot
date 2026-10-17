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

# Support up to 6 bot tokens (with fallback for user's configured bots)
BOT_TOKEN_1 = os.getenv("BOT_TOKEN_1", os.getenv("BOT_TOKEN", "8719226279:AAH3nWRh3-G1a3Gx2drYhhMrRqVH_gDGEag")).strip()
BOT_TOKEN_2 = os.getenv("BOT_TOKEN_2", "8637593283:AAFMVWWWytrcJKeXQhlXkiABU3EIt98XWyM").strip()
BOT_TOKEN_3 = os.getenv("BOT_TOKEN_3", "8862237272:AAESTK-s1T0iD7wHXFAqmCwbnhUPpG_ukbc").strip()
BOT_TOKEN_4 = os.getenv("BOT_TOKEN_4", "8805792544:AAGizRwhlgKD4uIL31P5EQHBcocnr4nkK_g").strip()
BOT_TOKEN_5 = os.getenv("BOT_TOKEN_5", "").strip()
BOT_TOKEN_6 = os.getenv("BOT_TOKEN_6", "").strip()

# Collect all configured tokens in order, strictly ensuring no duplicates
seen_tokens = set()
BOT_TOKENS = []
for t in [BOT_TOKEN_1, BOT_TOKEN_2, BOT_TOKEN_3, BOT_TOKEN_4, BOT_TOKEN_5, BOT_TOKEN_6]:
    if t and t not in seen_tokens:
        seen_tokens.add(t)
        BOT_TOKENS.append(t)



BOT_USERNAME = os.getenv("BOT_USERNAME", "anvarsave_bot").replace("@", "").strip()

DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Max file size Telegram Bot API can send directly (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# YouTube Cookies handling (bypasses Render/Cloud datacenter blocks)
YOUTUBE_COOKIES = os.getenv("YOUTUBE_COOKIES", "").strip()
LOCAL_COOKIES = BASE_DIR / "cookies.txt"
RENDER_SECRET_COOKIES = Path("/etc/secrets/cookies.txt")

def get_valid_cookies_path() -> Path | None:
    """Validate and normalize cookie file format so yt-dlp never crashes on malformed cookies"""
    header = "# Netscape HTTP Cookie File"
    
    # 1. Render secret file
    if RENDER_SECRET_COOKIES.exists():
        try:
            content = RENDER_SECRET_COOKIES.read_text(encoding="utf-8", errors="ignore")
            if "youtube.com" in content.lower():
                if header.lower() not in content.lower():
                    LOCAL_COOKIES.write_text(f"{header}\n{content}", encoding="utf-8")
                    return LOCAL_COOKIES
                return RENDER_SECRET_COOKIES
        except Exception:
            pass

    # 2. YOUTUBE_COOKIES environment variable
    if YOUTUBE_COOKIES and "youtube.com" in YOUTUBE_COOKIES.lower():
        try:
            content = YOUTUBE_COOKIES.strip()
            if header.lower() not in content.lower():
                content = f"{header}\n{content}"
            LOCAL_COOKIES.write_text(content, encoding="utf-8")
            return LOCAL_COOKIES
        except Exception:
            pass

    # 3. Local cookies.txt file
    if LOCAL_COOKIES.exists():
        try:
            content = LOCAL_COOKIES.read_text(encoding="utf-8", errors="ignore")
            if "youtube.com" in content.lower():
                if header.lower() not in content.lower():
                    LOCAL_COOKIES.write_text(f"{header}\n{content}", encoding="utf-8")
                return LOCAL_COOKIES
        except Exception:
            pass

    return None

COOKIES_PATH: Path | None = get_valid_cookies_path()

