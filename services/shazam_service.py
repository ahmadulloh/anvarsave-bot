import asyncio
import logging
from pathlib import Path
from shazamio import Shazam
import yt_dlp

logger = logging.getLogger(__name__)

class ShazamService:
    def __init__(self):
        self.shazam = Shazam()

    async def recognize_file(self, file_path: str | Path) -> dict | None:
        """
        Recognize song from audio/voice/video/video_note file using Shazam.
        """
        try:
            out = await self.shazam.recognize_song(str(file_path))
            track = out.get("track")
            if not track:
                return None

            title = track.get("title", "Unknown Title")
            subtitle = track.get("subtitle", "Unknown Artist")
            cover_url = track.get("images", {}).get("coverart")
            genres = track.get("genres", {}).get("primary", "")
            
            # Extract lyrics if available
            lyrics = None
            sections = track.get("sections", [])
            for s in sections:
                if s.get("type") == "LYRICS":
                    text_lines = s.get("text", [])
                    if text_lines:
                        lyrics = "\n".join(text_lines[:15])  # first 15 lines
                        break

            # Search corresponding YouTube ID for instant MP3 download
            yt_id = await self.find_best_youtube_match(f"{subtitle} {title}")

            return {
                "title": title,
                "subtitle": subtitle,
                "cover_url": cover_url,
                "genres": genres,
                "lyrics": lyrics,
                "yt_id": yt_id
            }
        except Exception as e:
            logger.error(f"Shazam recognition error: {e}")
            return None

    async def find_best_youtube_match(self, query: str) -> str | None:
        """Find the best YouTube video ID for a track"""
        loop = asyncio.get_running_loop()
        def _search():
            ydl_opts = {
                "quiet": True,
                "extract_flat": True,
                "noplaylist": True,
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    res = ydl.extract_info(f"ytsearch1:{query}", download=False)
                    entries = res.get("entries", [])
                    if entries:
                        return entries[0].get("id")
            except Exception:
                pass
            return None

        return await loop.run_in_executor(None, _search)

    async def search_tracks(self, query: str, limit: int = 5) -> list[dict]:
        """
        Search songs by title, artist, or lyrics using YouTube search
        """
        loop = asyncio.get_running_loop()

        def _search():
            results = []
            ydl_opts = {
                "quiet": True,
                "extract_flat": True,
                "noplaylist": True,
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    res = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
                    entries = res.get("entries", [])
                    for entry in entries:
                        duration = entry.get("duration")
                        duration_str = ""
                        if duration:
                            m, s = divmod(int(duration), 60)
                            duration_str = f"{m:02d}:{s:02d}"
                        
                        results.append({
                            "id": entry.get("id"),
                            "title": entry.get("title"),
                            "uploader": entry.get("uploader", ""),
                            "duration_str": duration_str,
                            "url": entry.get("url")
                        })
            except Exception as e:
                logger.error(f"Track search error: {e}")
            return results

        return await loop.run_in_executor(None, _search)

shazam_service = ShazamService()
