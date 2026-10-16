import re
from dataclasses import dataclass
from typing import Dict
from aiogram import Bot

def make_hashtag(name: str) -> str:
    """Format name into a clean Telegram hashtag, e.g. 'Mittivine' -> '#Mittivine'"""
    cleaned = re.sub(r"[^\w\s]", "", name).strip()
    return f"#{cleaned.replace(' ', '_')}" if cleaned else "#YouTube"

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

    def format_start(self, username: str) -> str:
        return self.start_text_template.format(bot_username=username)

    def format_help(self, username: str) -> str:
        return self.help_text_template.format(bot_username=username)

    def format_video_caption(self, username: str, title: str = "", author: str = "") -> str:
        if title and author and len(title) > 2 and author not in ["Instagram", "TikTok", "YouTube"]:
            tag = make_hashtag(author)
            footer = self.video_caption_template.format(bot_username=username, title=title, author=author)
            return f"📼 <b>{title[:50]} | {author} →</b>\n👤 {tag} →\n\n{footer}"
        return self.video_caption_template.format(bot_username=username, title=title, author=author)

    def format_youtube_caption(self, username: str, title: str = "", author: str = "") -> str:
        clean_title = title.strip() if title else "Video"
        clean_author = author.strip() if author else "YouTube"
        tag = make_hashtag(clean_author)
        footer = self.video_caption_template.format(bot_username=username, title=clean_title, author=clean_author)
        return f"📼 <b>{clean_title} | {clean_author} →</b>\n👤 {tag} →\n\n{footer}"

    def format_audio_caption(self, username: str, title: str = "", author: str = "") -> str:
        return self.audio_caption_template.format(bot_username=username, title=title, author=author)

# Preset profiles for the bots (Instagram, TikTok, YouTube video downloader)
PROFILES = [
    # Bot 1: Classic & Ishonchli (Anvar Save Bot)
    BotProfile(
        id=1,
        name="Anvar Save Bot",
        start_text_template=(
            "🔥 <b>Assalomu alaykum! @{bot_username} ga xush kelibsiz.</b>\n\n"
            "Bot orqali quyidagi tarmoqlardan videolarni oson va tez yuklab oling:\n\n"
            "• <b>Instagram</b> — Reels, postlar va videolar\n"
            "• <b>TikTok</b> — Suv belgisiz (HD sifatda)\n"
            "• <b>YouTube</b> — Shorts va to'liq videolar\n\n"
            "🚀 <i>Yuklab olish uchun video havolasini yuboring!</i>\n"
            "😎 <b>Bot guruhlarda ham to'liq ishlaydi!</b>"
        ),
        help_text_template=(
            "💡 <b>Botdan qanday foydalaniladi?</b>\n\n"
            "1️⃣ <b>Instagram, TikTok yoki YouTube</b> video havolasini botga yuboring.\n"
            "2️⃣ Bot videoni sizga darhol yuklab beradi.\n"
            "3️⃣ Videodagi qo'shiq kerak bo'lsa, video ostidagi '📩 Qo'shiqni yuklab olish' tugmasini bosing.\n\n"
            "👥 <i>Botni guruhlarga qo'shing va do'stlaringiz bilan qulay foydalaning!</i>"
        ),
        loading_text="⏳ <b>Yuklanmoqda...</b>",
        video_caption_template="📥 <b>@{bot_username}</b> orqali yuklab olindi",
        audio_caption_template="🎵 <b>{title}</b>\n📥 @{bot_username} orqali yuklab olindi",
        music_button_text="📩 Qo'shiqni yuklab olish",
        group_button_text="➕ Guruhga qo'shish ⤴"
    ),

    # Bot 2: Fast Saver / Ultra Tezkor
    BotProfile(
        id=2,
        name="Flash Saver Bot",
        start_text_template=(
            "⚡️ <b>Salom! @{bot_username} — Eng tezkor video yuklovchi bot.</b>\n\n"
            "Ijtimoiy tarmoqlardagi videolarni bir zumda, suv belgisiz va yuqori sifatda yuklab oling!\n\n"
            "📌 <b>Qo'llab-quvvatlanadi:</b>\n"
            "⚡️ <b>TikTok</b> — toza va suv belgisiz\n"
            "⚡️ <b>Instagram</b> — Reels, postlar va videolar\n"
            "⚡️ <b>YouTube</b> — Shorts va to'liq videolar\n\n"
            "⚡️ <i>Videoning havolasini tashlang!</i>"
        ),
        help_text_template=(
            "⚡️ <b>Tezkor yo'riqnoma:</b>\n\n"
            "• <b>Instagram, TikTok, YouTube</b> havolasini yuboring — bot tezda videoni tashlab beradi.\n"
            "• Videodagi musiqa kerak bo'lsa, '🎵 Musiqasini olish' tugmasini bosing.\n"
            "• Botni guruhlarga qo'shib, guruhdagilar uchun ham tezkor yuklashni yoqing!"
        ),
        loading_text="⚡️ <i>Tezkor yuklanmoqda...</i>",
        video_caption_template="⚡️ <b>@{bot_username}</b> bilan yuklandi",
        audio_caption_template="🎶 <b>{title}</b>\n⚡️ @{bot_username}",
        music_button_text="🎵 Musiqasini olish (MP3)",
        group_button_text="🚀 Guruhga ulash ⚡️"
    ),

    # Bot 3: Media Master Pro
    BotProfile(
        id=3,
        name="Media Master Pro",
        start_text_template=(
            "🎬 <b>Xush kelibsiz! @{bot_username} — Sifatli video yuklovchi.</b>\n\n"
            "Quyidagi tarmoqlardan videolarni yuqori sifatda yuklab oling:\n\n"
            "— <b>Instagram</b> (Reels, Postlar va videolar)\n"
            "— <b>TikTok</b> (Suv belgisiz toza video)\n"
            "— <b>YouTube</b> (Shorts va videolar)\n\n"
            "✨ <i>Istalgan video havolasini yuboring:</i>"
        ),
        help_text_template=(
            "🎬 <b>Foydalanish tartibi:</b>\n\n"
            "1️⃣ Video ssilkasini yuboring (Instagram, TikTok, YouTube).\n"
            "2️⃣ Videoni qabul qiling va tomosha qiling!\n"
            "3️⃣ Videodan audio ajratish uchun '🎧 Musiqani ko'chirish' tugmasini bosing."
        ),
        loading_text="🛰 <b>Tayyorlanmoqda, kuting...</b>",
        video_caption_template="🎬 <b>@{bot_username}</b> | Yuqori sifatda",
        audio_caption_template="🎧 <b>{title}</b>\n💎 @{bot_username}",
        music_button_text="🎧 Musiqani ko'chirish",
        group_button_text="🌐 Guruhga qo'shish ↗️"
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
