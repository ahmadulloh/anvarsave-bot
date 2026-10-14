import logging
from pathlib import Path
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, FSInputFile

from config import BOT_USERNAME
from services.downloader import get_or_extract_audio, download_youtube_audio

logger = logging.getLogger(__name__)
callback_router = Router()

@callback_router.callback_query(F.data.startswith("audio:"))
async def cb_download_audio(callback: CallbackQuery, bot: Bot):
    token = callback.data.split(":", 1)[1]
    await callback.answer("⏳ Qo'shiq tayyorlanmoqda, kuting...", show_alert=False)

    try:
        audio_info = await get_or_extract_audio(token)
        if not audio_info or not audio_info.get("audio_path"):
            await callback.message.reply("❌ Kechirasiz, videodan audio ajratib bo'lmadi.")
            return

        audio_path = audio_info["audio_path"]
        title = audio_info.get("title", "Audio")
        artist = audio_info.get("artist", f"@{BOT_USERNAME}")

        await callback.message.reply_audio(
            audio=FSInputFile(audio_path),
            title=title[:60],
            performer=artist[:60],
            caption=f"🎵 {title}\n📥 @{BOT_USERNAME} orqali yuklab olindi"
        )
    except Exception as e:
        logger.error(f"Error sending extracted audio: {e}")
        await callback.message.reply("❌ Musiqani yuborishda xatolik yuz berdi.")

@callback_router.callback_query(F.data.startswith("yt_dl:"))
async def cb_download_youtube_track(callback: CallbackQuery, bot: Bot):
    yt_id = callback.data.split(":", 1)[1]
    await callback.answer("⏳ Qo'shiq yuklanmoqda, kuting...", show_alert=False)

    status_msg = await callback.message.reply("⏳ <b>Qo'shiq yuklanmoqda...</b>", parse_mode="HTML")
    try:
        audio_info = await download_youtube_audio(yt_id)
        if not audio_info or not audio_info.get("audio_path"):
            await status_msg.edit_text("❌ Kechirasiz, musiqani yuklab bo'lmadi.")
            return

        audio_path = audio_info["audio_path"]
        title = audio_info.get("title", "Music")
        artist = audio_info.get("artist", f"@{BOT_USERNAME}")

        await callback.message.reply_audio(
            audio=FSInputFile(audio_path),
            title=title[:60],
            performer=artist[:60],
            caption=f"🎵 {title}\n📥 @{BOT_USERNAME} orqali yuklab olindi"
        )
        try:
            await status_msg.delete()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error downloading YouTube track: {e}")
        await status_msg.edit_text("❌ Musiqani yuklab olishda xatolik yuz berdi.")
