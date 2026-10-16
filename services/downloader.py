import asyncio
import hashlib
import json
import logging
import os
import re
import subprocess
import time
import uuid
from pathlib import Path
from urllib.parse import quote

import aiohttp
import yt_dlp

from config import DOWNLOAD_DIR, MAX_FILE_SIZE

logger = logging.getLogger(__name__)

# In-memory storage for media info to support "Qo'shiqni yuklab olish" button
MEDIA_CACHE: dict[str, dict] = {}

# Reusable client session for high performance & connection pooling
_HTTP_SESSION: aiohttp.ClientSession | None = None

async def get_http_session() -> aiohttp.ClientSession:
    """Return a pooled aiohttp session for faster downloads"""
    global _HTTP_SESSION
    if _HTTP_SESSION is None or _HTTP_SESSION.closed:
        timeout = aiohttp.ClientTimeout(total=45, connect=10)
        connector = aiohttp.TCPConnector(limit=50, keepalive_timeout=30)
        _HTTP_SESSION = aiohttp.ClientSession(timeout=timeout, connector=connector)
    return _HTTP_SESSION

async def close_http_session():
    """Close the pooled session on shutdown"""
    global _HTTP_SESSION
    if _HTTP_SESSION and not _HTTP_SESSION.closed:
        await _HTTP_SESSION.close()
        _HTTP_SESSION = None

# Regex patterns for supported platforms
URL_PATTERNS = {
    "tiktok": re.compile(r"https?://(?:[a-zA-Z0-9_-]+\.)?tiktok\.com/[^\s]+", re.IGNORECASE),
    "instagram": re.compile(r"https?://(?:www\.)?instagram\.com/(?:reel|reels|p|tv|share)/[^\s]+", re.IGNORECASE),
    "youtube": re.compile(r"https?://(?:www\.)?(?:youtube\.com/(?:watch\?v=|shorts/|embed/)|youtu\.be/)[a-zA-Z0-9_-]+[^\s]*", re.IGNORECASE),
    "pinterest": re.compile(r"https?://(?:[a-zA-Z0-9]+\.)?(?:pinterest\.com/pin/|pin\.it/)[^\s]+", re.IGNORECASE),
    "likee": re.compile(r"https?://(?:[a-zA-Z0-9]+\.)?likee\.video/[^\s]+", re.IGNORECASE),
    "snapchat": re.compile(r"https?://(?:www\.)?snapchat\.com/[^\s]+", re.IGNORECASE),
}

def detect_platform(url: str) -> str | None:
    """Detect platform from URL"""
    for platform, pattern in URL_PATTERNS.items():
        if pattern.search(url):
            return platform
    return None

def extract_first_url(text: str) -> str | None:
    """Extract first supported media URL from text"""
    for pattern in URL_PATTERNS.values():
        m = pattern.search(text)
        if m:
            return m.group(0).split("?")[0] if "instagram.com" in m.group(0) or "tiktok.com" in m.group(0) else m.group(0)
    return None

async def download_file_from_url(url: str, dest_path: Path, headers: dict | None = None) -> bool:
    """Download a file asynchronously using aiohttp with fast chunking"""
    try:
        session = await get_http_session()
        req_headers = headers or {"User-Agent": "Mozilla/5.0"}
        async with session.get(url, headers=req_headers, timeout=aiohttp.ClientTimeout(total=45)) as resp:
            if resp.status == 200:
                with open(dest_path, "wb") as f:
                    while True:
                        chunk = await resp.content.read(1024 * 256)  # 256KB buffer for max speed
                        if not chunk:
                            break
                        f.write(chunk)
                return dest_path.exists() and dest_path.stat().st_size > 0
    except Exception as e:
        logger.error(f"Error downloading {url} to {dest_path}: {e}")
    return False

def check_video_has_audio(file_path: str | Path) -> bool:
    """Check if video file contains an audio stream using ffprobe"""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_type",
            "-of", "csv=p=0",
            str(file_path)
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8)
        output = res.stdout.decode().lower().strip()
        return "audio" in output
    except Exception as e:
        logger.debug(f"ffprobe check failed: {e}")
        return True  # Fallback to True if check fails

def extract_audio_from_video(video_path: str | Path, output_path: str | Path) -> bool:
    """Extract MP3 audio from video using ffmpeg subprocess with fast encoding"""
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vn",
            "-acodec", "libmp3lame",
            "-q:a", "4",  # Fast ~165kbps VBR audio
            "-threads", "0",
            str(output_path)
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=25)
        return res.returncode == 0 and Path(output_path).exists() and Path(output_path).stat().st_size > 0
    except Exception as e:
        logger.error(f"ffmpeg extraction failed: {e}")
        return False

# ================= TIKTOK DOWNLOADER =================
async def download_tiktok(url: str) -> dict | None:
    """Download TikTok video without watermark using TikWM API"""
    api_url = f"https://www.tikwm.com/api/?url={url}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        session = await get_http_session()
        async with session.get(api_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get("code") == 0:
                    d = data.get("data", {})
                    video_url = d.get("play") or d.get("hdplay") or d.get("wmplay")
                    music_url = d.get("music")
                    title = d.get("title", "") or "TikTok Video"
                    author = d.get("author", {}).get("nickname", "TikTok")
                    duration = d.get("duration", 0)

                    if video_url:
                        file_id = f"tiktok_{uuid.uuid4().hex[:10]}"
                        dest_video = DOWNLOAD_DIR / f"{file_id}.mp4"
                        success = await download_file_from_url(video_url, dest_video, headers)
                        if success:
                            token = uuid.uuid4().hex[:12]
                            has_audio = bool(music_url) or check_video_has_audio(dest_video)
                            MEDIA_CACHE[token] = {
                                "video_path": str(dest_video),
                                "audio_url": music_url,
                                "audio_path": None,
                                "title": title,
                                "artist": author,
                                "has_audio": has_audio,
                                "created_at": time.time(),
                            }
                            return {
                                "media_type": "video",
                                "file_path": str(dest_video),
                                "title": title,
                                "author": author,
                                "duration": duration,
                                "token": token,
                                "has_audio": has_audio
                            }
    except Exception as e:
        logger.warning(f"TikWM error, falling back to yt-dlp: {e}")

    # Fallback to yt-dlp
    return await download_with_ytdlp(url, platform="tiktok")

# ================= INSTAGRAM DOWNLOADER =================
async def download_instagram(url: str) -> dict | None:
    """Download Instagram Reel / Post / IGTV using GraphQL endpoint"""
    m = re.search(r"instagram\.com/(?:reel|reels|p|tv|share)/([^/?#&]+)", url)
    if not m:
        return await download_with_ytdlp(url, platform="instagram")
    
    shortcode = m.group(1)
    variables = quote(json.dumps({"shortcode": shortcode}))
    payload = f"variables={variables}&doc_id=24368985919464652"
    headers = {
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "x-csrftoken": "YuvV-QRvpR2Ggzgk0cTg1T",
        "x-ig-app-id": "936619743392459",
        "Cookie": "csrftoken=YuvV-QRvpR2Ggzgk0cTg1T; mid=aOia4gALAAHSq3em2E34YEIFkMCC"
    }

    try:
        session = await get_http_session()
        async with session.post("https://www.instagram.com/graphql/query", headers=headers, data=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                d = await resp.json()
                items = d.get("data", {}).get("xdt_api__v1__media__shortcode__web_info", {}).get("items", [])
                if items:
                    item = items[0]
                    video_versions = item.get("video_versions", [])
                    caption_node = item.get("caption", {}) or {}
                    title = caption_node.get("text", "") if isinstance(caption_node, dict) else ""
                    author = item.get("user", {}).get("username", "Instagram")
                    
                    # If video is present
                    if video_versions:
                        video_url = video_versions[0].get("url")
                        file_id = f"ig_{shortcode}_{uuid.uuid4().hex[:6]}"
                        dest_video = DOWNLOAD_DIR / f"{file_id}.mp4"
                        success = await download_file_from_url(video_url, dest_video)
                        if success:
                            token = uuid.uuid4().hex[:12]
                            has_audio = check_video_has_audio(dest_video)
                            MEDIA_CACHE[token] = {
                                "video_path": str(dest_video),
                                "audio_url": None,
                                "audio_path": None,
                                "title": title[:40] if title else "Instagram Reel",
                                "artist": author,
                                "has_audio": has_audio,
                                "created_at": time.time(),
                            }
                            return {
                                "media_type": "video",
                                "file_path": str(dest_video),
                                "title": title[:50] if title else "Instagram Video",
                                "author": author,
                                "token": token,
                                "has_audio": has_audio
                            }
                    
                    # If photo / image
                    candidates = item.get("image_versions2", {}).get("candidates", [])
                    if candidates:
                        img_url = candidates[0].get("url")
                        file_id = f"ig_{shortcode}_{uuid.uuid4().hex[:6]}"
                        dest_img = DOWNLOAD_DIR / f"{file_id}.jpg"
                        success = await download_file_from_url(img_url, dest_img)
                        if success:
                            token = uuid.uuid4().hex[:12]
                            return {
                                "media_type": "photo",
                                "file_path": str(dest_img),
                                "title": title[:50] if title else "Instagram Photo",
                                "author": author,
                                "token": token,
                                "has_audio": False
                            }
    except Exception as e:
        logger.warning(f"Instagram GraphQL error, trying fallback: {e}")

    return await download_with_ytdlp(url, platform="instagram")

def get_ffmpeg_path() -> str | None:
    """Find valid ffmpeg executable location"""
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()
    except Exception:
        pass
    import shutil
    return shutil.which("ffmpeg")

# ================= GENERAL YT-DLP DOWNLOADER =================
def _run_ytdlp_download(url: str, outtmpl: str, is_audio: bool = False) -> tuple[dict | None, str | None]:
    """Synchronous yt-dlp worker with robust formats and ffmpeg integration"""
    ffmpeg_bin = get_ffmpeg_path()

    base_opts = {
        "outtmpl": outtmpl,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "socket_timeout": 30,
        "nocheckcertificate": True,
    }
    if ffmpeg_bin:
        base_opts["ffmpeg_location"] = ffmpeg_bin

    from config import COOKIES_PATH
    if COOKIES_PATH and COOKIES_PATH.exists():
        base_opts["cookiefile"] = str(COOKIES_PATH)

    last_error_str = None

    if is_audio:
        audio_formats = [
            "bestaudio/best",
            "ba/b",
        ]
        for fmt in audio_formats:
            ydl_opts = dict(base_opts)
            ydl_opts["format"] = fmt
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if info:
                        return info, None
            except Exception as e:
                err_msg = str(e)
                logger.warning(f"yt-dlp audio download with '{fmt}' failed: {err_msg}")
                if "Sign in to confirm you" in err_msg or "bot" in err_msg.lower():
                    last_error_str = "bot_detection"
        return None, last_error_str
    else:
        # Prioritize 720p HD so downloaded video stays within Telegram's 50MB limit
        video_formats = [
            "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]/best",
            "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]/best",
            "best[filesize<=48M]/best",
        ]
        for fmt in video_formats:
            ydl_opts = dict(base_opts)
            ydl_opts["format"] = fmt
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if info:
                        return info, None
            except Exception as e:
                err_msg = str(e)
                logger.warning(f"yt-dlp video download with '{fmt}' failed: {err_msg}")
                if "Sign in to confirm you" in err_msg or "bot" in err_msg.lower():
                    last_error_str = "bot_detection"
        return None, last_error_str

async def download_with_ytdlp(url: str, platform: str = "general") -> dict:
    """Asynchronous wrapper for fast yt-dlp download"""
    loop = asyncio.get_running_loop()
    file_id = f"{platform}_{uuid.uuid4().hex[:10]}"
    outtmpl = str(DOWNLOAD_DIR / f"{file_id}.%(ext)s")

    info, err = await loop.run_in_executor(None, _run_ytdlp_download, url, outtmpl, False)
    if not info:
        return {"file_path": None, "error": err}

    # Find the downloaded file
    files = list(DOWNLOAD_DIR.glob(f"{file_id}.*"))
    if not files:
        return {"file_path": None, "error": err}

    downloaded_file = files[0]
    ext = downloaded_file.suffix.lower()
    media_type = "photo" if ext in [".jpg", ".jpeg", ".png", ".webp"] else "video"

    title = info.get("title", "") or "Media"
    author = info.get("uploader", "") or info.get("channel", "") or platform.capitalize()
    duration = info.get("duration", 0)

    token = uuid.uuid4().hex[:12]
    has_audio = check_video_has_audio(downloaded_file) if media_type == "video" else False
    MEDIA_CACHE[token] = {
        "video_path": str(downloaded_file) if media_type == "video" else None,
        "audio_url": None,
        "audio_path": None,
        "title": title,
        "artist": author,
        "has_audio": has_audio,
        "created_at": time.time(),
    }

    return {
        "media_type": media_type,
        "file_path": str(downloaded_file),
        "title": title,
        "author": author,
        "duration": duration,
        "token": token,
        "has_audio": has_audio
    }

# ================= AUDIO EXTRACTOR / DOWNLOADER =================
async def get_or_extract_audio(token: str) -> dict | None:
    """Extract or download audio from cache token with audio availability check"""
    media_info = MEDIA_CACHE.get(token)
    if not media_info:
        return None

    # If already verified to have no audio stream, immediately return None
    if not media_info.get("has_audio", True):
        return None

    # Check if audio already extracted
    audio_path = media_info.get("audio_path")
    if audio_path and Path(audio_path).exists():
        return {
            "audio_path": audio_path,
            "title": media_info.get("title", "Audio"),
            "artist": media_info.get("artist", "")
        }

    # If direct music URL was saved (e.g. from TikTok)
    audio_url = media_info.get("audio_url")
    if audio_url:
        dest_audio = DOWNLOAD_DIR / f"audio_{token}.mp3"
        success = await download_file_from_url(audio_url, dest_audio)
        if success:
            media_info["audio_path"] = str(dest_audio)
            return {
                "audio_path": str(dest_audio),
                "title": media_info.get("title", "Audio"),
                "artist": media_info.get("artist", "")
            }

    # Extract audio from video file using fast ffmpeg
    video_path = media_info.get("video_path")
    if video_path and Path(video_path).exists():
        dest_audio = DOWNLOAD_DIR / f"audio_{token}.mp3"
        loop = asyncio.get_running_loop()
        success = await loop.run_in_executor(None, extract_audio_from_video, video_path, dest_audio)
        if success:
            media_info["audio_path"] = str(dest_audio)
            return {
                "audio_path": str(dest_audio),
                "title": media_info.get("title", "Audio"),
                "artist": media_info.get("artist", "")
            }
        else:
            media_info["has_audio"] = False

    return None

async def download_youtube_audio(yt_id_or_url: str) -> dict | None:
    """Download YouTube audio as MP3"""
    if yt_id_or_url.startswith("http"):
        url = yt_id_or_url
    else:
        url = f"https://www.youtube.com/watch?v={yt_id_or_url}"

    loop = asyncio.get_running_loop()
    file_id = f"ytaudio_{uuid.uuid4().hex[:10]}"
    outtmpl = str(DOWNLOAD_DIR / f"{file_id}.%(ext)s")

    info, err = await loop.run_in_executor(None, _run_ytdlp_download, url, outtmpl, True)
    if not info:
        return {"audio_path": None, "error": err}

    # Find the resulting mp3
    expected_path = DOWNLOAD_DIR / f"{file_id}.mp3"
    if expected_path.exists():
        return {
            "audio_path": str(expected_path),
            "title": info.get("title", "Music"),
            "artist": info.get("uploader", "") or info.get("channel", ""),
            "duration": info.get("duration", 0)
        }
    
    # Check any generated file with that id
    files = list(DOWNLOAD_DIR.glob(f"{file_id}.*"))
    if files:
        return {
            "audio_path": str(files[0]),
            "title": info.get("title", "Music"),
            "artist": info.get("uploader", "") or info.get("channel", ""),
            "duration": info.get("duration", 0)
        }

    return {"audio_path": None, "error": err}

async def download_media(url: str) -> dict | None:
    """Master entry point for downloading media from supported platforms"""
    platform = detect_platform(url)
    if not platform:
        return None

    logger.info(f"Downloading {platform} media: {url}")
    if platform == "tiktok":
        return await download_tiktok(url)
    elif platform == "instagram":
        return await download_instagram(url)
    elif platform == "youtube":
        return await download_with_ytdlp(url, platform="youtube")
    elif platform == "pinterest":
        return await download_with_ytdlp(url, platform="pinterest")
    elif platform == "likee":
        return await download_with_ytdlp(url, platform="likee")
    elif platform == "snapchat":
        return await download_with_ytdlp(url, platform="snapchat")
    else:
        return await download_with_ytdlp(url, platform="general")

def cleanup_old_files(max_age_seconds: int = 1200):
    """Delete downloaded files older than max_age_seconds to free disk space"""
    now = time.time()
    try:
        for file in DOWNLOAD_DIR.glob("*"):
            if file.is_file() and file.name != ".gitkeep":
                if now - file.stat().st_mtime > max_age_seconds:
                    try:
                        file.unlink()
                    except Exception:
                        pass
        # Clean memory cache
        expired_tokens = [k for k, v in MEDIA_CACHE.items() if now - v.get("created_at", 0) > max_age_seconds]
        for k in expired_tokens:
            MEDIA_CACHE.pop(k, None)
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
