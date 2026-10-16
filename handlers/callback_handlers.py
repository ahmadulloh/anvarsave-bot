import logging
from pathlib import Path
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, FSInputFile

from services.downloader import get_or_extract_audio, download_youtube_audio
from utils.bot_profiles import get_bot_profile, get_bot_username

logger = logging.getLogger(__name__)
callback_router = Router()

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

@callback_router.callback_query(F.data.startswith("yt_dl:"))
async def cb_download_youtube_track(callback: CallbackQuery, bot: Bot):
    yt_id = callback.data.split(":", 1)[1]
    profile = get_bot_profile(bot)
    username = await get_bot_username(bot)
    await callback.answer("⏳ Qo'shiq yuklanmoqda, kuting...", show_alert=False)

    status_msg = await callback.message.reply("⏳ <b>Qo'shiq yuklanmoqda...</b>", parse_mode="HTML")
    try:
        audio_info = await download_youtube_audio(yt_id)
        if not audio_info or not audio_info.get("audio_path"):
            err = audio_info.get("error") if audio_info else None
            if err == "bot_detection":
                await status_msg.edit_text(
                    "⚠️ <b>YouTube serveri audio yuklashni chekladi (Bot tekshiruvi).</b>\n\n"
                    "💡 Render sozlamalariga <code>YOUTUBE_COOKIES</code> (cookies.txt) qo'shilishi lozim.",
                    parse_mode="HTML"
                )
            else:
                await status_msg.edit_text("❌ Kechirasiz, musiqani yuklab bo'lmadi.")
            return

        audio_path = audio_info["audio_path"]
        title = audio_info.get("title") or "Music"
        artist = audio_info.get("artist") or f"@{username}"

        caption = profile.format_audio_caption(username, title=title, author=artist)

        await callback.message.reply_audio(
            audio=FSInputFile(audio_path),
            title=title[:60],
            performer=artist[:60],
            caption=caption,
            parse_mode="HTML"
        )
        try:
            await status_msg.delete()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error downloading YouTube track: {e}")
        await status_msg.edit_text("❌ Musiqani yuklab olishda xatolik yuz berdi.")
