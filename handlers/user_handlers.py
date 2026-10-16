import logging
import uuid
from pathlib import Path

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile

from config import DOWNLOAD_DIR, MAX_FILE_SIZE
from services.downloader import (
    extract_first_url,
    download_media,
    get_or_extract_audio
)
from services.shazam_service import shazam_service
from utils.bot_profiles import get_bot_profile, get_bot_username
from utils.keyboards import (
    get_start_keyboard,
    get_video_keyboard,
    get_shazam_keyboard,
    get_search_results_keyboard
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

    # If message contains a media URL
    if url:
        profile = get_bot_profile(bot)
        username = await get_bot_username(bot)
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

    # If it's a private chat and not a command: Music Search (by name/artist/lyrics)
    if message.chat.type == "private":
        if text.startswith("/"):
            return
        
        search_msg = await message.reply(f"🔎 <b>'{text}'</b> qidirilmoqda...", parse_mode="HTML")
        try:
            tracks = await shazam_service.search_tracks(text, limit=5)
            if not tracks:
                await search_msg.edit_text(
                    "😕 <b>Hech qanday musiqa topilmadi.</b>\nBoshqacha nom yoki ijrochini yozib ko'ring.",
                    parse_mode="HTML"
                )
                return

            res_text = f"🎶 <b>'{text}' bo'yicha topilgan qo'shiqlar:</b>\n\n"
            for idx, t in enumerate(tracks, 1):
                dur = f" ({t['duration_str']})" if t.get('duration_str') else ""
                res_text += f"{idx}. <b>{t['title']}</b>{dur}\n"

            res_text += "\n<i>Yuklab olish uchun quyidagi tugmalardan birini bosing:</i>"
            await search_msg.edit_text(res_text, reply_markup=get_search_results_keyboard(tracks), parse_mode="HTML")
        except Exception as e:
            logger.error(f"Search error: {e}")
            await search_msg.edit_text("❌ Qidiruvda xatolik yuz berdi.", parse_mode="HTML")

# ================= SHAZAM RECOGNITION HANDLER (AUDIO, VOICE, VIDEO, VIDEO_NOTE) =================
@user_router.message(F.voice | F.video_note | F.audio | F.video)
async def handle_shazam_media(message: Message, bot: Bot):
    # In groups, only recognize if replied to bot or starts with /shazam
    if message.chat.type != "private":
        caption = message.caption or ""
        if not (caption.startswith("/shazam") or (message.reply_to_message and message.reply_to_message.from_user.id == bot.id)):
            return

    status_msg = await message.reply("🔍 <b>Qo'shiq aniqlanmoqda (Shazam)...</b>", parse_mode="HTML")

    file_id = None
    if message.voice:
        file_id = message.voice.file_id
        ext = "ogg"
    elif message.video_note:
        file_id = message.video_note.file_id
        ext = "mp4"
    elif message.audio:
        file_id = message.audio.file_id
        ext = "mp3"
    elif message.video:
        file_id = message.video.file_id
        ext = "mp4"

    if not file_id:
        await status_msg.edit_text("❌ Faylni o'qib bo'lmadi.")
        return

    temp_path = DOWNLOAD_DIR / f"shazam_{uuid.uuid4().hex[:8]}.{ext}"
    try:
        tg_file = await bot.get_file(file_id)
        await bot.download_file(tg_file.file_path, destination=temp_path)

        result = await shazam_service.recognize_file(temp_path)
        if not result:
            await status_msg.edit_text(
                "😕 <b>Qo'shiq aniqlanmadi.</b>\nIltimos, aniqroq yoki musiqasi balandroq qismini yuboring.",
                parse_mode="HTML"
            )
            return

        title = result.get("title", "")
        subtitle = result.get("subtitle", "")
        genres = result.get("genres", "")
        lyrics = result.get("lyrics")
        cover_url = result.get("cover_url")
        yt_id = result.get("yt_id")

        profile = get_bot_profile(bot)
        username = await get_bot_username(bot)

        reply_text = (
            f"🎵 <b>{title}</b>\n"
            f"👤 <b>Ijrochi:</b> {subtitle}\n"
        )
        if genres:
            reply_text += f"🎸 <b>Janr:</b> {genres}\n"
        if lyrics:
            reply_text += f"\n📝 <b>Qo'shiq matni:</b>\n<i>{lyrics}</i>\n"

        reply_text += f"\n📥 @{username}"

        # Send with cover photo if available
        if cover_url:
            try:
                await message.reply_photo(
                    photo=cover_url,
                    caption=reply_text,
                    reply_markup=get_shazam_keyboard(yt_id, profile=profile, bot_username=username),
                    parse_mode="HTML"
                )
                await status_msg.delete()
                return
            except Exception:
                pass

        await status_msg.edit_text(
            reply_text,
            reply_markup=get_shazam_keyboard(yt_id, profile=profile, bot_username=username),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Shazam processing error: {e}")
        await status_msg.edit_text("❌ Musiqani aniqlashda xatolik yuz berdi.", parse_mode="HTML")
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
