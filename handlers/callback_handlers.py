import logging
from pathlib import Path
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, FSInputFile

from services.downloader import get_or_extract_audio, download_youtube
from utils.bot_profiles import get_bot_profile, get_bot_username
from utils.keyboards import get_youtube_video_keyboard
from config import MAX_FILE_SIZE

logger = logging.getLogger(__name__)
callback_router = Router()

# ================= YOUTUBE VIDEO HANDLER (SaqlaBot UI) =================
@callback_router.callback_query(F.data.startswith("yt:v:"))
async def cb_youtube_video(callback: CallbackQuery, bot: Bot):
    video_id = callback.data.split(":", 2)[2]
    profile = get_bot_profile(bot)
    username = await get_bot_username(bot)
    await callback.answer("⏳ Video yuklanmoqda, kuting...", show_alert=False)

    status_msg = await callback.message.reply(profile.loading_text, parse_mode="HTML")
    try:
        res = await download_youtube(video_id, is_audio=False)
        if not res or not res.get("file_path"):
            err = res.get("error") if res else None
            if err == "bot_detection":
                await status_msg.edit_text(
                    "⚠️ <b>YouTube serveri so'rovni chekladi (Bot himoyasi).</b>\n\n"
                    "💡 Render/serverda YouTube videolarni yuklash uchun <code>YOUTUBE_COOKIES</code> (cookies.txt) talab qilinadi.",
                    parse_mode="HTML"
                )
            else:
                await status_msg.edit_text("❌ <b>Videoni yuklab bo'lmadi.</b>", parse_mode="HTML")
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
        caption = profile.format_youtube_caption(username, title=title, author=author)

        await callback.message.reply_video(
            video=FSInputFile(file_path),
            caption=caption,
            reply_markup=get_youtube_video_keyboard(video_id, profile=profile, bot_username=username),
            parse_mode="HTML"
        )
        try:
            await status_msg.delete()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error handling YouTube video {video_id}: {e}")
        await status_msg.edit_text("❌ <b>Xatolik yuz berdi.</b> Qaytadan urinib ko'ring.", parse_mode="HTML")

# ================= YOUTUBE AUDIO HANDLER (SaqlaBot UI) =================
@callback_router.callback_query(F.data.startswith("yt:a:"))
async def cb_youtube_audio(callback: CallbackQuery, bot: Bot):
    video_id = callback.data.split(":", 2)[2]
    profile = get_bot_profile(bot)
    username = await get_bot_username(bot)
    await callback.answer("⏳ Audio tayyorlanmoqda, kuting...", show_alert=False)

    status_msg = await callback.message.reply("⏳ <b>Audio tayyorlanmoqda...</b>", parse_mode="HTML")
    try:
        res = await download_youtube(video_id, is_audio=True)
        if not res or not res.get("file_path"):
            await status_msg.edit_text("❌ <b>Audioni yuklab bo'lmadi.</b>", parse_mode="HTML")
            return

        file_path = res["file_path"]
        title = res.get("title", "") or "Audio"
        author = res.get("author", "") or f"@{username}"
        caption = profile.format_youtube_caption(username, title=title, author=author)

        await callback.message.reply_audio(
            audio=FSInputFile(file_path),
            title=title[:60],
            performer=author[:60],
            caption=caption,
            parse_mode="HTML"
        )
        try:
            await status_msg.delete()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error handling YouTube audio {video_id}: {e}")
        await status_msg.edit_text("❌ <b>Xatolik yuz berdi.</b> Qaytadan urinib ko'ring.", parse_mode="HTML")

# ================= VIDEO AUDIO EXTRACTION (Instagram & TikTok) =================
@callback_router.callback_query(F.data.startswith("audio:"))
async def cb_download_audio(callback: CallbackQuery, bot: Bot):
    token = callback.data.split(":", 1)[1]
    profile = get_bot_profile(bot)
    username = await get_bot_username(bot)
    await callback.answer("⏳ Qo'shiq tayyorlanmoqda, kuting...", show_alert=False)

    try:
        audio_info = await get_or_extract_audio(token)
        if not audio_info or not audio_info.get("audio_path"):
            await callback.answer("❌ Bu videoda musiqa yoki audio mavjud emas.", show_alert=True)
            return

        audio_path = audio_info["audio_path"]
        title = audio_info.get("title") or "Audio"
        artist = audio_info.get("artist") or f"@{username}"

        caption = profile.format_audio_caption(username, title=title, author=artist)

        await callback.message.reply_audio(
            audio=FSInputFile(audio_path),
            title=title[:60],
            performer=artist[:60],
            caption=caption,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error sending extracted audio: {e}")
        await callback.answer("❌ Musiqani yuklashda xatolik yuz berdi.", show_alert=True)

