from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.bot_profiles import BotProfile, PROFILES

def get_start_keyboard(profile: BotProfile | None = None, bot_username: str = "bot") -> InlineKeyboardMarkup:
    """Start message inline keyboard with dynamic text and link per bot"""
    p = profile or PROFILES[0]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=p.group_button_text,
                    url=f"https://t.me/{bot_username}?startgroup=true"
                )
            ]
        ]
    )
    return keyboard

def get_video_keyboard(
    media_token: str,
    profile: BotProfile | None = None,
    bot_username: str = "bot",
    has_audio: bool = True
) -> InlineKeyboardMarkup:
    """
    Keyboard attached below downloaded video.
    If video has audio, presents distinct audio extraction button.
    If video does not have audio, shows only group button.
    """
    p = profile or PROFILES[0]
    buttons = []

    if has_audio:
        buttons.append([
            InlineKeyboardButton(
                text=p.music_button_text,
                callback_data=f"audio:{media_token}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text=p.group_button_text,
            url=f"https://t.me/{bot_username}?startgroup=true"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
