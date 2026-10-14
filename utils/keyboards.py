from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_USERNAME

def get_start_keyboard() -> InlineKeyboardMarkup:
    """Start message inline keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Guruhga qo'shish ⤴",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
                )
            ]
        ]
    )
    return keyboard

def get_video_keyboard(media_token: str) -> InlineKeyboardMarkup:
    """Keyboard attached below every downloaded video"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📩 Qo'shiqni yuklab olish",
                    callback_data=f"audio:{media_token}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Guruhga qo'shish ⤴",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
                )
            ]
        ]
    )
    return keyboard

def get_shazam_keyboard(yt_id: str | None = None) -> InlineKeyboardMarkup:
    """Keyboard for recognized Shazam song"""
    buttons = []
    if yt_id:
        buttons.append([
            InlineKeyboardButton(
                text="📥 Qo'shiqni yuklab olish (MP3)",
                callback_data=f"yt_dl:{yt_id}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text="Guruhga qo'shish ⤴",
            url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_search_results_keyboard(items: list[dict]) -> InlineKeyboardMarkup:
    """Inline keyboard for YouTube / Shazam track search results"""
    buttons = []
    for idx, item in enumerate(items, 1):
        yt_id = item.get("id")
        title = item.get("title", f"Track {idx}")
        duration = item.get("duration_str", "")
        btn_text = f"{idx}. 📥 {title[:32]} ({duration})" if duration else f"{idx}. 📥 {title[:36]}"
        buttons.append([
            InlineKeyboardButton(
                text=btn_text,
                callback_data=f"yt_dl:{yt_id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
