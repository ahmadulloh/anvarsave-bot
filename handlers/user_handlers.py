import logging
import uuid
from pathlib import Path

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile

from config import BOT_USERNAME, DOWNLOAD_DIR
from services.downloader import (
    extract_first_url,
    download_media,
    get_or_extract_audio
)
from services.shazam_service import shazam_service
from utils.keyboards import (
    get_start_keyboard,
    get_video_keyboard,
    get_shazam_keyboard,
    get_search_results_keyboard
)

logger = logging.getLogger(__name__)
user_router = Router()

START_TEXT = (
    "🔥 <b>Assalomu alaykum! @{bot_username} ga xush kelibsiz.</b>\n\n"
    "Bot orqali quyidagilarni yuklab olishingiz mumkin:\n\n"
    "• <b>Instagram</b> - post, reels va IGTV + audio;\n"
    "• <b>TikTok</b> - suv belgisiz video + audio;\n"
    "• <b>YouTube</b> - videolar va shorts + audio;\n"
    "• <b>Snapchat</b> - suv belgisiz video + audio;\n"
    "• <b>Likee</b> - suv belgisiz video + audio;\n"
    "• <b>Pinterest</b> - video va rasmlar + audio;\n\n"
    "🎵 <b>Shazam funksiyasi:</b>\n"
    "• Qo‘shiq nomi yoki ijrochi ismi (yozib yuboring)\n"
    "• Qo‘shiq matni (she'rini yozib yuboring)\n"
    "• Ovozli xabar (voice)\n"
    "• Video va Dumaloq video xabar (video note)\n"
    "• Audio fayl\n\n"
    "🚀 <i>Yuklab olmoqchi bo'lgan videoga havolani yuboring!</i>\n"
    "😎 <b>Bot guruhlarda ham bemalol ishlaydi!</b>"
)

@user_router.message(CommandStart())
async def cmd_start(message: Message):
    text = START_TEXT.format(bot_username=BOT_USERNAME)
    await message.answer(text, reply_markup=get_start_keyboard(), parse_mode="HTML")

@user_router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "💡 <b>Botdan qanday foydalanish mumkin?</b>\n\n"
        "1️⃣ <b>Video yuklab olish:</b> Istalgan Instagram, TikTok, YouTube, Pinterest, Likee yoki Snapchat havolasini yuboring.\n"
        "2️⃣ <b>Musiqa topish (Shazam):</b> Ovozli xabar, video, audio yoki video xabar (dumaloq video) yuboring.\n"
        "3️⃣ <b>Qo'shiq nomi/matni:</b> Qo'shiq nomini yoki matnidan bir qator yozib yuboring.\n\n"
        "👥 <b>Guruhlarda ishlatish:</b> Botni guruhga qo'shing va admin qiling. Guruhdagi istalgan havolalarni bot o'zi avtomatik yuklab beradi!"
    )
    await message.answer(text, reply_markup=get_start_keyboard(), parse_mode="HTML")

# ================= LINK HANDLER =================
@user_router.message(F.text)
async def handle_text(message: Message, bot: Bot):
    text = message.text.strip()
    url = extract_first_url(text)

    # If message contains a media URL
    if url:
        status_msg = await message.reply("⏳ <b>Yuklanmoqda...</b>", parse_mode="HTML")
        try:
            res = await download_media(url)
            if not res or not res.get("file_path"):
                await status_msg.edit_text("❌ <b>Kechirasiz, videoni yuklab bo'lmadi.</b>\nHavola to'g'riligini yoki video ochiqligini tekshiring.", parse_mode="HTML")
                return

            file_path = res["file_path"]
            caption = res.get("caption", f"📥 @{BOT_USERNAME} orqali yuklab olindi")
            media_type = res.get("media_type", "video")
            token = res.get("token")

            if media_type == "video":
                await message.reply_video(
                    video=FSInputFile(file_path),
                    caption=caption,
                    reply_markup=get_video_keyboard(token) if token else None
                )
            elif media_type == "photo":
                await message.reply_photo(
                    photo=FSInputFile(file_path),
                    caption=caption
                )
            elif media_type == "audio":
                await message.reply_audio(
                    audio=FSInputFile(file_path),
                    caption=caption
                )

            # Delete the "Yuklanmoqda..." status message
            try:
                await status_msg.delete()
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Error handling URL {url}: {e}")
            await status_msg.edit_text("❌ <b>Xatolik yuz berdi.</b> Iltimos, qaytadan urinib ko'ring.", parse_mode="HTML")
        return

    # If it's a private chat and not a command: Treat as Music Search (by name/artist/lyrics)
    if message.chat.type == "private":
        if text.startswith("/"):
            return
        
        search_msg = await message.reply(f"🔎 <b>'{text}'</b> qidirilmoqda...", parse_mode="HTML")
        try:
            tracks = await shazam_service.search_tracks(text, limit=5)
            if not tracks:
                await search_msg.edit_text("😕 <b>Hech qanday musiqa topilmadi.</b>\nBoshqacha nom yoki ijrochini yozib ko'ring.", parse_mode="HTML")
                return

            res_text = f"🎶 <b>'{text}' bo'yicha topilgan qo'shiqlar:</b>\n\n"
            for idx, t in enumerate(tracks, 1):
                dur = f" ({t['duration_str']})" if t['duration_str'] else ""
                res_text += f"{idx}. <b>{t['title']}</b>{dur}\n"

            res_text += "\n<i>Yuklab olish uchun quyidagi tugmalardan birini bosing:</i>"
            await search_msg.edit_text(res_text, reply_markup=get_search_results_keyboard(tracks), parse_mode="HTML")
        except Exception as e:
            logger.error(f"Search error: {e}")
            await search_msg.edit_text("❌ Qidiruvda xatolik yuz berdi.", parse_mode="HTML")

# ================= SHAZAM RECOGNITION HANDLER (AUDIO, VOICE, VIDEO, VIDEO_NOTE) =================
@user_router.message(F.voice | F.video_note | F.audio | F.video)
async def handle_shazam_media(message: Message, bot: Bot):
    # In groups, only recognize if message is replied to bot or has caption /shazam
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
            await status_msg.edit_text("😕 <b>Qo'shiq aniqlanmadi.</b>\nIltimos, aniqroq yoki musiqasi balandroq qismini yuboring.", parse_mode="HTML")
            return

        title = result.get("title", "")
        subtitle = result.get("subtitle", "")
        genres = result.get("genres", "")
        lyrics = result.get("lyrics")
        cover_url = result.get("cover_url")
        yt_id = result.get("yt_id")

        reply_text = (
            f"🎵 <b>{title}</b>\n"
            f"👤 <b>Ijrochi:</b> {subtitle}\n"
        )
        if genres:
            reply_text += f"🎸 <b>Janr:</b> {genres}\n"
        if lyrics:
            reply_text += f"\n📝 <b>Qo'shiq matni:</b>\n<i>{lyrics}</i>\n"

        reply_text += f"\n📥 @{BOT_USERNAME}"

        # Send with cover photo if available
        if cover_url:
            try:
                await message.reply_photo(
                    photo=cover_url,
                    caption=reply_text,
                    reply_markup=get_shazam_keyboard(yt_id),
                    parse_mode="HTML"
                )
                await status_msg.delete()
                return
            except Exception:
                pass

        await status_msg.edit_text(reply_text, reply_markup=get_shazam_keyboard(yt_id), parse_mode="HTML")

    except Exception as e:
        logger.error(f"Shazam processing error: {e}")
        await status_msg.edit_text("❌ Musiqani aniqlashda xatolik yuz berdi.", parse_mode="HTML")
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
