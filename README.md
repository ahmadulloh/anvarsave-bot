# 🚀 Multi-Bot Tezkor Video Yuklovchi (Instagram, TikTok, YouTube)

Ushbu bot bir vaqtning o'zida bir nechta botlarni parallel ishlatish imkoniyatiga ega bo'lgan, Instagram, TikTok va YouTube tarmoqlaridan videolarni eng yuqori sifatda yuklab beruvchi Telegram bot hisoblanadi.

---

## 🌟 Botning Asosiy Imkoniyatlari

### 🎬 Ijtimoiy Tarmoqlardan Video Yuklash
- **Instagram**: Reels, postlar va videolar;
- **TikTok**: Suv belgisiz (no watermark) eng yuqori sifatli video;
- **YouTube**: Shorts va videolar (720p HD);
- Har bir yuklangan video ostida uning audiosini alohida yuklab olish imkoniyati.

---

### 3. 👥 Guruhlarda Ishlash Imkoniyati
Botni istalgan guruhga qo'shish mumkin. Guruh a'zolari havola tashlaganda, bot darhol videoni guruhga yuklab beradi.

> ⚠️ **Muhim eslatma (Guruhlar uchun):**
> Telegramda bot guruhdagi barcha xabarlarni ko'rishi uchun [@BotFather](https://t.me/BotFather) ga kiring:
> 1. `/mybots` ni bosing va `@anvarsave_bot` ni tanlang.
> 2. **Bot Settings** -> **Group Privacy** -> **Turn off** qiling.
> 3. Shunda bot guruhga admin qilinmasa ham barcha havolalarni avtomatik taniydi!

---

## 💻 Kompyuterda Ishga Tushirish (Lokal)

1. Kutubxonalarni o'rnatish:
```bash
pip install -r requirements.txt
```

2. `.env` faylida token to'g'riligini tekshiring:
```env
BOT_TOKEN=8719226279:AAH3nWRh3-G1a3Gx2drYhhMrRqVH_gDGEag
BOT_USERNAME=anvarsave_bot
```

3. Botni ishga tushirish:
```bash
python bot.py
```

---

## 🐙 1-QADAM: Loyihani GitHub'ga Yuklash

Botni serverga ulash uchun avval uni GitHub profilingizga yuklaysiz.

1. [GitHub.com](https://github.com) saytiga kiring va yangi repository oching (masalan: `anvarsave-bot`, **Public** qilib).
2. Kompyuteringizda ushbu loyiha papkasida terminal oching va quyidagi buyruqlarni ketma-ket tering:

```bash
git init
git add .
git commit -m "Initial commit for @anvarsave_bot"
git branch -M main
git remote add origin https://github.com/SIZNING_GITHUBINGIZ/anvarsave-bot.git
git push -u origin main
```
*(Eslatma: `SIZNING_GITHUBINGIZ` o'rniga o'zingizning GitHub username'ingizni yozing).*

---

## ☁️ 2-QADAM: Bepul Serverga 24/7 Joylash (Doim Ishlashi Uchun)

Quyidagi 2 ta eng qulay bepul hostingdan birini tanlashingiz mumkin:

---

### Variant 1: Koyeb (Tavsiya etiladi - 100% Bepul va FFmpeg/Docker qo'llab-quvvatlaydi)

1. [Koyeb.com](https://www.koyeb.com/) saytiga kiring va GitHub orqali ro'yxatdan o'ting.
2. **Create App** tugmasini bosing.
3. Deployment method sifatida **GitHub** ni tanlang.
4. O'zingiz ochgan `anvarsave-bot` repository'sini tanlang.
5. Builder sifatida **Dockerfile** ni tanlang (loyihada tayyor Dockerfile bor).
6. **Environment Variables** bo'limida qo'shing:
   - `BOT_TOKEN`: `8719226279:AAH3nWRh3-G1a3Gx2drYhhMrRqVH_gDGEag`
   - `BOT_USERNAME`: `anvarsave_bot`
7. **Instance Type**: **Nano** (Free tier) ni tanlang.
8. **Deploy** tugmasini bosing. 2-3 daqiqada botingiz 24/7 serverda ishga tushadi!

---

### Variant 2: Render.com (Bepul Background Worker)

1. [Render.com](https://render.com/) saytiga kiring va GitHub orqali kiring.
2. **New +** tugmasini bosing -> **Background Worker** ni tanlang.
3. GitHub'dagi `anvarsave-bot` repozitoriyangizni tanlang.
4. Sozlamalari:
   - **Environment**: `Docker`
   - **Branch**: `main`
   - **Plan**: `Free`
5. **Environment Variables** ga qo'shing:
   - `BOT_TOKEN` = `8719226279:AAH3nWRh3-G1a3Gx2drYhhMrRqVH_gDGEag`
   - `BOT_USERNAME` = `anvarsave_bot`
6. **Create Worker** tugmasini bosing. Bo'ldi, bot 24/7 doimiy ishlab turadi!

---

### Variant 3: O'z VPS (Linux / Ubuntu) serveringizda Docker bilan ishga tushirish

Agar sizda VPS server bo'lsa:
```bash
git clone https://github.com/SIZNING_GITHUBINGIZ/anvarsave-bot.git
cd anvarsave-bot
docker-compose up -d --build
```

---

## 📁 Loyiha Strukturasi

```
Anvar avto save bot/
├── bot.py                  # Botni ishga tushiruvchi asosiy fayl
├── config.py               # Token va sozlamalar
├── requirements.txt        # Kerakli Python kutubxonalari
├── Dockerfile              # Docker konteyneri (ffmpeg bilan)
├── docker-compose.yml      # VPS uchun docker-compose
├── render.yaml             # Render.com avtomatik deployment fayli
├── Procfile                # Hosting jarayonlar fayli
├── .env                    # Maxfiy tokenlar
├── .env.example            # Token namunasi
├── .gitignore              # Git uchun istisno fayllar
├── handlers/
│   ├── user_handlers.py    # Start, yordam, link yuklash va Shazam
│   └── callback_handlers.py# Tugmalar (MP3 yuklab olish)
├── services/
│   ├── downloader.py       # TikWM, Instagram, YouTube, Pinterest yuklovchisi
│   └── shazam_service.py   # Shazam va musiqa qidiruv tizimi
└── utils/
    └── keyboards.py        # Chiroyli inline tugmalar
```

---
Muallif: **@anvarsave_bot** uchun tayyorlandi.
