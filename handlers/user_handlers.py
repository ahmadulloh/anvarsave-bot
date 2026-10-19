import logging
from pathlib import Path

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, URLInputFile

from config import DOWNLOAD_DIR, MAX_FILE_SIZE
from services.downloader import (
    extract_first_url,
    detect_platform,
    extract_youtube_video_id,
    get_youtube_preview_info,
    download_media
)
from utils.bot_profiles import get_bot_profile, get_bot_username
from utils.keyboards import (
    get_start_keyboard,
    get_video_keyboard,
    get_youtube_preview_keyboard
)

logger = logging.getLogger(__name__)
user_router = Router()

# ================= START & HELP COMMANDS =================
@user_router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    profile = get_bot_profile(bot)
    username = await get_bot_username(bot)
    text = profile.format_start(username)
    await message.answer(text, reply_markup=get_start_keyboard(profile, username), parse_mode="HTML")

@user_router.message(Command("help"))
async def cmd_help(message: Message, bot: Bot):
    profile = get_bot_profile(bot)
    username = await get_bot_username(bot)
    text = profile.format_help(username)
    await message.answer(text, reply_markup=get_start_keyboard(profile, username), parse_mode="HTML")

# ================= LINK & TEXT HANDLER =================
@user_router.message(F.text)
async def handle_text(message: Message, bot: Bot):
    text = message.text.strip()
    url = extract_first_url(text)

    # If message contains a media URL (Instagram, TikTok, YouTube, etc.)
    if url:
        profile = get_bot_profile(bot)
        username = await get_bot_username(bot)
        platform = detect_platform(url)

        # YouTube UI: If direct_youtube_download is True (e.g. Akbarjon Media Bot), bypass the format preview card
        # and download the video directly at maximum speed!
        if platform == "youtube" and not profile.direct_youtube_download:
            video_id = extract_youtube_video_id(url)
            if not video_id:
                await message.reply("❌ <b>YouTube havolasi yaroqsiz.</b>", parse_mode="HTML")
                return

            yt_info = await get_youtube_preview_info(video_id)
            title = yt_info.get("title", "YouTube Video")
            author = yt_info.get("author", "YouTube")
            thumb_url = yt_info.get("thumbnail_url", f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg")

            caption = f"📼 <b>{title} | {author} →</b>{profile.yt_format_text}"
            keyboard = get_youtube_preview_keyboard(video_id, profile=profile)

            try:
                await message.reply_photo(
                    photo=URLInputFile(thumb_url),
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.warning(f"URLInputFile photo send error: {e}")
                try:
                    await message.reply_photo(
                        photo=thumb_url,
                        caption=caption,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
                except Exception as e2:
                    logger.error(f"Fallback photo send error: {e2}")
                    await message.reply(
                        caption,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
            return

        status_msg = await message.reply(profile.loading_text, parse_mode="HTML")
        try:
            res = await download_media(url)
            if not res or not res.get("file_path"):
                err = res.get("error") if res else None
                if err == "bot_detection":
                    await status_msg.edit_text(
                        "⚠️ <b>YouTube serveri so'rovni chekladi (Bot himoyasi).</b>\n\n"
                        "💡 Render/serverda YouTube videolarni yuklash uchun <code>YOUTUBE_COOKIES</code> (cookies.txt) talab qilinadi.\n"
                        "Instagram va TikTok esa cheklovlarsiz ishlayveradi.",
                        parse_mode="HTML"
                    )
                else:
                    await status_msg.edit_text(
                        "❌ <b>Kechirasiz, videoni yuklab bo'lmadi.</b>\nHavola to'g'riligini yoki video ochiqligini tekshiring.",
                        parse_mode="HTML"
                    )
                return

            file_path = res["file_path"]
            file_size = Path(file_path).stat().st_size
            if file_size > MAX_FILE_SIZE:
                await status_msg.edit_text(
                    f"⚠️ <b>Video hajmi juda katta ({round(file_size / (1024 * 1024), 1)} MB).</b>\n"
                    "Telegram Bot orqali faqat 50 MB gacha bo'lgan videolarni yuborish mumkin.",
                    parse_mode="HTML"
                )
                return

            title = res.get("title", "")
            author = res.get("author", "")
            media_type = res.get("media_type", "video")
            token = res.get("token")
            has_audio = res.get("has_audio", True)

            if platform == "youtube":
                caption = profile.format_youtube_caption(username, title=title, author=author)
            else:
                caption = profile.format_video_caption(username, title=title, author=author)

            if media_type == "video":
                await message.reply_video(
                    video=FSInputFile(file_path),
                    caption=caption,
                    reply_markup=get_video_keyboard(token, profile=profile, bot_username=username, has_audio=has_audio) if token else None,
                    parse_mode="HTML"
                )
            elif media_type == "photo":
                await message.reply_photo(
                    photo=FSInputFile(file_path),
                    caption=caption,
                    parse_mode="HTML"
                )
            elif media_type == "audio":
                await message.reply_audio(
                    audio=FSInputFile(file_path),
                    caption=caption,
                    parse_mode="HTML"
                )

            # Delete the loading status message
            try:
                await status_msg.delete()
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Error handling URL {url}: {e}")
            await status_msg.edit_text("❌ <b>Xatolik yuz berdi.</b> Iltimos, qaytadan urinib ko'ring.", parse_mode="HTML")
        return

    # If it's a private chat and not a command or link: Ask for video link
    if message.chat.type == "private":
        if text.startswith("/"):
            return
        
        await message.reply(
            "🚀 <b>Iltimos, video havolasini yuboring!</b>\n\n"
            "📌 <b>Qo'llab-quvvatlanadi:</b>\n"
            "• <b>Instagram</b> (Reels, postlar)\n"
            "• <b>TikTok</b> (Suv belgisiz HD)\n"
            "• <b>YouTube</b> (Shorts, videolar)",
            parse_mode="HTML"
        )
