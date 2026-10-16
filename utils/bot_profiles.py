from dataclasses import dataclass
from typing import Dict
from aiogram import Bot

@dataclass
class BotProfile:
    id: int
    name: str
    start_text_template: str
    help_text_template: str
    loading_text: str
    video_caption_template: str
    audio_caption_template: str
    music_button_text: str
    group_button_text: str
    shazam_dl_button_text: str

    def format_start(self, username: str) -> str:
        return self.start_text_template.format(bot_username=username)

    def format_help(self, username: str) -> str:
        return self.help_text_template.format(bot_username=username)

    def format_video_caption(self, username: str, title: str = "", author: str = "") -> str:
        return self.video_caption_template.format(bot_username=username, title=title, author=author)

    def format_audio_caption(self, username: str, title: str = "", author: str = "") -> str:
        return self.audio_caption_template.format(bot_username=username, title=title, author=author)

# Preset profiles for the 3 bots
PROFILES = [
    # Bot 1: Classic & Ishonchli (Anvar Save Bot)
    BotProfile(
        id=1,
        name="Anvar Save Bot",
        start_text_template=(
            "🔥 <b>Assalomu alaykum! @{bot_username} ga xush kelibsiz.</b>\n\n"
            "Bot orqali quyidagi tarmoqlardan video va musiqalarni oson yuklab oling:\n\n"
            "• <b>Instagram</b> — post, reels, IGTV + audio\n"
            "• <b>TikTok</b> — suv belgisiz (HD) + audio\n"
            "• <b>YouTube</b> — video va shorts + audio\n"
            "• <b>Snapchat, Likee, Pinterest</b>\n\n"
            "🎵 <b>Shazam imkoniyati:</b>\n"
            "• Qo'shiq nomi yoki matnini yozib yuboring\n"
            "• Ovozli xabar (voice), video yoki audio yuboring\n\n"
            "🚀 <i>Yuklab olmoqchi bo'lgan video havolasini yuboring!</i>\n"
            "😎 <b>Bot guruhlarda ham to'liq ishlaydi!</b>"
        ),
        help_text_template=(
            "💡 <b>Botdan qanday foydalaniladi?</b>\n\n"
            "1️⃣ <b>Video yuklash:</b> Instagram, TikTok, YouTube, Pinterest havolasini yuboring.\n"
            "2️⃣ <b>Musiqa yuklash:</b> Video ostidagi tugma orqali uning audiosini alohida yuklab oling.\n"
            "3️⃣ <b>Shazam:</b> Qo'shiq nomi, ovozli xabar yoki video yuboring va to'liq musiqasini oling.\n\n"
            "👥 <i>Botni guruhlarga qo'shing va do'stlaringiz bilan qulay foydalaning!</i>"
        ),
        loading_text="⏳ <b>Yuklanmoqda...</b>",
        video_caption_template="📥 <b>@{bot_username}</b> orqali yuklab olindi",
        audio_caption_template="🎵 <b>{title}</b>\n📥 @{bot_username} orqali yuklab olindi",
        music_button_text="📩 Qo'shiqni yuklab olish",
        group_button_text="➕ Guruhga qo'shish ⤴",
        shazam_dl_button_text="📥 Qo'shiqni yuklab olish (MP3)"
    ),

    # Bot 2: Fast Saver / Ultra Tezkor (Zamonaviy va chaqqon uslub)
    BotProfile(
        id=2,
        name="Flash Saver Bot",
        start_text_template=(
            "⚡️ <b>Salom! @{bot_username} — Eng tezkor media yuklovchi bot.</b>\n\n"
            "Ijtimoiy tarmoqlardagi videolarni bir zumda, suv belgisiz va yuqori sifatda yuklab oling!\n\n"
            "📌 <b>Qo'llab-quvvatlanadi:</b>\n"
            "⚡️ <b>TikTok</b> — toza va suv belgisiz\n"
            "⚡️ <b>Instagram</b> — Reels, postlar va videolar\n"
            "⚡️ <b>YouTube</b> — Shorts va to'liq videolar\n"
            "⚡️ <b>Pinterest, Likee, Snapchat</b>\n\n"
            "⚡️ <i>Shunchaki video havolasini tashlang!</i>"
        ),
        help_text_template=(
            "⚡️ <b>Tezkor yo'riqnoma:</b>\n\n"
            "• Istalgan video havolasini botga yuboring — bot soniyalar ichida videoni tashlab beradi.\n"
            "• Videodagi musiqa kerak bo'lsa, '🎵 Musiqasini olish' tugmasini bosing.\n"
            "• Botni guruhlarga qo'shib, guruhdagilar uchun ham tezkor yuklashni yoqing!"
        ),
        loading_text="⚡️ <i>Tezkor yuklanmoqda...</i>",
        video_caption_template="⚡️ <b>@{bot_username}</b> bilan yuklandi",
        audio_caption_template="🎶 <b>{title}</b>\n⚡️ @{bot_username}",
        music_button_text="🎵 Musiqasini olish (MP3)",
        group_button_text="🚀 Guruhga ulash ⚡️",
        shazam_dl_button_text="⚡️ MP3 yuklab olish"
    ),

    # Bot 3: Smart Media & Music Pro (Premium barchasi bittada)
    BotProfile(
        id=3,
        name="Media & Music Pro",
        start_text_template=(
            "💎 <b>Xush kelibsiz! @{bot_username} — Universal media va musiqa boti.</b>\n\n"
            "🎬 <b>Universal Video Saver:</b>\n"
            "— Instagram, TikTok, YouTube, Likee, Pinterest\n"
            "— Videolardan musiqani alohida ajratib olish imkoniyati\n\n"
            "🎧 <b>Smart Music Finder (Shazam):</b>\n"
            "— Qo'shiq nomi, ijrochi yoki so'zlari bo'yicha qidiruv\n"
            "— Ovozli xabar (voice) yoki videodan qo'shiqni aniqlash\n\n"
            "✨ <i>Istalgan video havolasi yoki musiqani yuboring:</i>"
        ),
        help_text_template=(
            "💎 <b>Foydalanish tartibi:</b>\n\n"
            "🎬 <b>Video yuklash:</b> Havolani yuboring -> Videoni oling -> '🎧 Musiqani ko'chirish' orqali audiosini yuklang.\n"
            "🎧 <b>Shazam:</b> Ovozli xabar yoki video yuboring va to'liq trekni MP3 formatda oling.\n"
            "🌐 <i>Guruhga admin qilib qo'shsangiz, havolalarni avtomatik ushlaydi.</i>"
        ),
        loading_text="🛰 <b>Tayyorlanmoqda, kuting...</b>",
        video_caption_template="🎬 <b>@{bot_username}</b> | Yuqori sifatda",
        audio_caption_template="🎧 <b>{title}</b>\n💎 @{bot_username}",
        music_button_text="🎧 Musiqani ko'chirish",
        group_button_text="🌐 Guruhga qo'shish ↗️",
        shazam_dl_button_text="🎧 MP3 ni ko'chirib olish"
    ),
]

_TOKEN_PROFILE_MAP: Dict[str, BotProfile] = {}
_BOT_ID_PROFILE_MAP: Dict[int, BotProfile] = {}
_BOT_USERNAME_MAP: Dict[int, str] = {}

def register_bot_profile(bot_token: str, profile_index: int, bot_id: int | None = None, username: str | None = None):
    """Register a bot token and map it to a specific profile (0-indexed or 1-indexed)"""
    idx = profile_index % len(PROFILES)
    profile = PROFILES[idx]
    _TOKEN_PROFILE_MAP[bot_token] = profile
    if bot_id:
        _BOT_ID_PROFILE_MAP[bot_id] = profile
    if bot_id and username:
        _BOT_USERNAME_MAP[bot_id] = username

def get_bot_profile(bot: Bot) -> BotProfile:
    """Retrieve the distinct profile for this bot instance"""
    if bot.id in _BOT_ID_PROFILE_MAP:
        return _BOT_ID_PROFILE_MAP[bot.id]
    if bot.token in _TOKEN_PROFILE_MAP:
        return _TOKEN_PROFILE_MAP[bot.token]
    return PROFILES[0]

async def get_bot_username(bot: Bot) -> str:
    """Get bot username with in-memory caching to prevent redundant API calls"""
    if bot.id in _BOT_USERNAME_MAP:
        return _BOT_USERNAME_MAP[bot.id]
    try:
        me = await bot.get_me()
        if me.username:
            _BOT_USERNAME_MAP[bot.id] = me.username
            return me.username
    except Exception:
        pass
    return "bot"
