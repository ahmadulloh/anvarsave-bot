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

# Preset profiles for the 6 distinct bots (Instagram, TikTok, YouTube video downloader)
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
            "3️⃣ Videodagi qo'shiq kerak bo'lsa, '📩 Qo'shiqni yuklab olish' tugmasini bosing.\n\n"
            "👥 <i>Botni guruhlarga qo'shing va do'stlaringiz bilan qulay foydalaning!</i>"
        ),
        loading_text="⏳ <b>Yuklanmoqda...</b>",
        video_caption_template="📥 <b>@{bot_username}</b> orqali yuklab olindi",
        audio_caption_template="🎵 <b>{title}</b>\n📥 @{bot_username} orqali yuklab olindi",
        music_button_text="📩 Qo'shiqni yuklab olish",
        group_button_text="➕ Guruhga qo'shish ⤴"
    ),

    # Bot 2: Maftuna Save Bot (Nafis & Chiroyli)
    BotProfile(
        id=2,
        name="Maftuna Save",
        start_text_template=(
            "🌸 <b>Salom! @{bot_username} ga xush kelibsiz.</b>\n\n"
            "Ijtimoiy tarmoqlardagi sevimli videolaringizni bir zumda va toza sifatda saqlab oling:\n\n"
            "✨ <b>Instagram</b> — Reels, Stories va videolar\n"
            "✨ <b>TikTok</b> — Suv belgisiz original sifat\n"
            "✨ <b>YouTube</b> — Shorts va to'liq videolar\n\n"
            "🎀 <i>Shunchaki video ssilkasini yuboring!</i>\n"
            "🌸 <b>Guruhlarga qo'shib, do'stlaringiz bilan birga ishlating!</b>"
        ),
        help_text_template=(
            "🌸 <b>Foydalanish bo'yicha ko'rsatma:</b>\n\n"
            "• Istalgan <b>Instagram, TikTok yoki YouTube</b> havolasini tashlang.\n"
            "• Bot bir necha soniyada videoni tayyorlab beradi.\n"
            "• Videodagi musiqa kerak bo'lsa, '🎧 Musiqasini yuklash' tugmasini bosing."
        ),
        loading_text="🌸 <b>Tayyorlanmoqda, kuting...</b>",
        video_caption_template="🎀 <b>@{bot_username}</b> orqali saqlandi",
        audio_caption_template="🎶 <b>{title}</b>\n🎀 @{bot_username}",
        music_button_text="🎧 Musiqasini yuklash",
        group_button_text="🌸 Guruhga qo'shish ✨"
    ),

    # Bot 3: Zeboxon Downloader (Ultra Tezkor & Energetik)
    BotProfile(
        id=3,
        name="Zeboxon Downloader",
        start_text_template=(
            "⚡️ <b>Salom! @{bot_username} — Ultra tezkor video yuklovchi.</b>\n\n"
            "Ijtimoiy tarmoqlardagi videolarni bir zumda, suv belgisiz va yuqori HD sifatda oling!\n\n"
            "📌 <b>Qo'llab-quvvatlanadi:</b>\n"
            "⚡️ <b>TikTok</b> — toza va suv belgisiz\n"
            "⚡️ <b>Instagram</b> — Reels, postlar va videolar\n"
            "⚡️ <b>YouTube</b> — Shorts va to'liq videolar\n\n"
            "🚀 <i>Video havolasini tashlang!</i>"
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

    # Bot 4: Muborakxon Save (Premium & Elegant)
    BotProfile(
        id=4,
        name="Muborakxon Save",
        start_text_template=(
            "💎 <b>Xush kelibsiz! @{bot_username} — Sifatli media yuklovchi.</b>\n\n"
            "Videolarni original tiniqligida, hech qanday qiyinchiliksiz saqlang:\n\n"
            "💠 <b>Instagram</b> — Reels, postlar va IGTV\n"
            "💠 <b>TikTok</b> — Asl HD sifatda, suv belgisiz\n"
            "💠 <b>YouTube</b> — Shorts va sifatli videolar\n\n"
            "💎 <i>Video ssilkasini yuboring:</i>"
        ),
        help_text_template=(
            "💎 <b>Qanday ishlatiladi?</b>\n\n"
            "1️⃣ Instagram, TikTok yoki YouTube havolasini yuboring.\n"
            "2️⃣ Sifatli videoni qabul qilib oling.\n"
            "3️⃣ Audio uchun '🎶 Trekni ko'chirish' tugmasidan foydalaning."
        ),
        loading_text="💎 <b>Sifatli formatda tayyorlanmoqda...</b>",
        video_caption_template="💎 <b>@{bot_username}</b> | Premium Saver",
        audio_caption_template="💎 <b>{title}</b>\n💎 @{bot_username}",
        music_button_text="🎶 Trekni ko'chirish",
        group_button_text="🌐 Guruhga qo'shish 💎"
    ),

    # Bot 5: Siadmx Yuklovchi
    BotProfile(
        id=5,
        name="Siadmx Yuklovchi",
        start_text_template=(
            "⚡️ <b>Assalomu alaykum! @{bot_username} xizmatingizda.</b>\n\n"
            "Ijtimoiy tarmoqlardagi videolarni eng yuqori sifatda va tezkor saqlab oling:\n\n"
            "🔥 <b>Instagram</b> — Reels, postlar va videolar\n"
            "🔥 <b>TikTok</b> — Suv belgisiz toza sifat\n"
            "🔥 <b>YouTube</b> — Shorts va to'liq videolar\n\n"
            "🚀 <i>Yuklash uchun video havolasini yuboring!</i>"
        ),
        help_text_template=(
            "⚡️ <b>Foydalanish bo'yicha ko'rsatma:</b>\n\n"
            "1️⃣ Video ssilkasini yuboring (Instagram, TikTok, YouTube).\n"
            "2️⃣ Videoni bir zumda qabul qiling!\n"
            "3️⃣ Musiqa kerak bo'lsa, '🎵 Musiqasini yuklash' tugmasini bosing."
        ),
        loading_text="⚡️ <b>Tezkor yuklanmoqda...</b>",
        video_caption_template="📥 <b>@{bot_username}</b> orqali yuklandi",
        audio_caption_template="🎧 <b>{title}</b>\n⚡️ @{bot_username}",
        music_button_text="🎵 Musiqasini yuklash",
        group_button_text="➕ Guruhga qo'shish 🚀"
    ),

    # Bot 6: Axmadullo Saqla Bot
    BotProfile(
        id=6,
        name="Axmadullo Saqla Bot",
        start_text_template=(
            "🌟 <b>Salom! @{bot_username} ga xush kelibsiz!</b>\n\n"
            "Videolarni tez, qulay va original tiniq sifatda saqlab oling:\n\n"
            "✨ <b>Instagram</b> — Reels, videolar va stories\n"
            "✨ <b>TikTok</b> — Suv belgisiz original HD\n"
            "✨ <b>YouTube</b> — Shorts va to'liq videolar\n\n"
            "📌 <i>Boshlash uchun video ssilkasini yuboring!</i>\n"
            "👥 <b>Guruhlarga qo'shib, birga foydalaning!</b>"
        ),
        help_text_template=(
            "🌟 <b>Yo'riqnoma:</b>\n\n"
            "• Video havolasini botga tashlang.\n"
            "• Bot darhol videoni yuklab beradi.\n"
            "• Audiosini olish uchun '🎧 Audio trekni olish' tugmasini bosing."
        ),
        loading_text="🌟 <b>Tayyorlanmoqda, kuting...</b>",
        video_caption_template="🌟 <b>@{bot_username}</b> bilan saqlandi",
        audio_caption_template="🎵 <b>{title}</b>\n🌟 @{bot_username}",
        music_button_text="🎧 Audio trekni olish",
        group_button_text="👥 Guruhga qo'shish 🌟"
    ),

    # Bot 7: Nasiba Save (Yumshoq & Go'zal uslub)
    BotProfile(
        id=7,
        name="Nasiba Save",
        start_text_template=(
            "🌺 <b>Salom! @{bot_username} ga xush kelibsiz.</b>\n\n"
            "Ijtimoiy tarmoqlardagi videolarni tez va sifatli formatda saqlab oling:\n\n"
            "🌷 <b>Instagram</b> — Reels, postlar va videolar\n"
            "🌷 <b>TikTok</b> — Suv belgisiz original HD\n"
            "🌷 <b>YouTube</b> — Shorts va to'liq formatdagi videolar\n\n"
            "💖 <i>Videoni yuklash uchun shunchaki havolasini yuboring!</i>\n"
            "🌺 <b>Guruhlarga ham qo'shishingiz mumkin!</b>"
        ),
        help_text_template=(
            "🌺 <b>Foydalanish tartibi:</b>\n\n"
            "• Video havolasini botga yuboring (Instagram, TikTok yoki YouTube).\n"
            "• Bot bir necha soniyada videoni tayyorlab beradi.\n"
            "• Qo'shig'ini olish uchun '🎧 Qo'shig'ini yuklash' tugmasini bosing."
        ),
        loading_text="🌺 <b>Yuklanmoqda, iltimos kuting...</b>",
        video_caption_template="💖 <b>@{bot_username}</b> orqali saqlandi",
        audio_caption_template="🎶 <b>{title}</b>\n💖 @{bot_username}",
        music_button_text="🎧 Qo'shig'ini yuklash",
        group_button_text="🌺 Guruhga qo'shish ✨"
    ),
]

_TOKEN_PROFILE_MAP: Dict[str, BotProfile] = {}
_BOT_ID_PROFILE_MAP: Dict[int, BotProfile] = {}
_BOT_USERNAME_MAP: Dict[int, str] = {}

def register_bot_profile(bot_token: str, profile_index: int, bot_id: int | None = None, username: str | None = None):
    """Register a bot token and map it to a specific profile (auto-matched by username or index)"""
    idx = profile_index % len(PROFILES)
    if username:
        u = username.lower()
        if "anvar" in u:
            idx = 0
        elif "maftuna" in u:
            idx = 1
        elif "zeboxon" in u:
            idx = 2
        elif "muborak" in u:
            idx = 3
        elif "siadmx" in u or "yukla" in u:
            idx = 4
        elif "axmadullo" in u or "saqla" in u:
            idx = 5
        elif "nasiba" in u:
            idx = 6

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
