import asyncio
import logging
import os
import sys

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKENS
from handlers.user_handlers import user_router
from handlers.callback_handlers import callback_router
from services.downloader import cleanup_old_files, close_http_session
from utils.bot_profiles import register_bot_profile, PROFILES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("multi_save_bot")

async def periodic_cleanup():
    """Periodically remove downloaded files older than 15 minutes"""
    while True:
        try:
            await asyncio.sleep(600)  # every 10 minutes
            cleanup_old_files(max_age_seconds=900)
            logger.info("Periodic cleanup finished.")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in cleanup loop: {e}")

async def start_web_server(active_bot_names: list[str]):
    """Lightweight health check web server to keep bots alive on Render/Koyeb Free Tier"""
    async def handle_ping(request):
        bots_str = ", ".join(f"@{name}" for name in active_bot_names)
        return web.Response(
            text=f"Active Bots ({len(active_bot_names)}): {bots_str} running 24/7!",
            status=200
        )

    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)

    port = int(os.getenv("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health-check web server started on port {port}")
    return runner

async def main():
    if os.getenv("RENDER"):
        logger.warning("⚠️ RENDER muhiti aniqlandi. Ushbu botlar to'liq Eskiz VPS (77.83.206.138) serveriga ko'chirilgan!")
        logger.warning("TelegramConflictError bo'lmasligi uchun Render-da Telegram polling o'chirildi. Render faqat veb-server rejimida ishlaydi.")
        web_runner = await start_web_server(["Eskiz_VPS_ga_ko'chirilgan_77.83.206.138"])
        try:
            await asyncio.Event().wait()
        finally:
            await web_runner.cleanup()
        return

    if not BOT_TOKENS:
        logger.error("Hech qanday BOT_TOKEN topilmadi! .env faylini tekshiring.")
        sys.exit(1)

    dp = Dispatcher()

    # Register routers (shared by all bots)
    dp.include_router(callback_router)
    dp.include_router(user_router)

    valid_bots: list[Bot] = []
    bot_names: list[str] = []
    seen_bot_ids: set[int] = set()

    # Initialize each configured bot (preventing any duplicate bot instances)
    for idx, token in enumerate(BOT_TOKENS):
        bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            me = await bot.get_me()

            if me.id in seen_bot_ids:
                logger.warning(
                    f"⚠️ Bot #{idx + 1} (@{me.username}, id={me.id}) dublikat bot! Bitta botni bir nechta o'zgaruvchiga qo'shib bo'lmaydi. O'tkazib yuborildi."
                )
                await bot.session.close()
                continue

            seen_bot_ids.add(me.id)
            profile = PROFILES[len(valid_bots) % len(PROFILES)]
            register_bot_profile(token, len(valid_bots), bot_id=me.id, username=me.username)
            valid_bots.append(bot)
            bot_names.append(me.username)
            logger.info(
                f"✅ Bot #{len(valid_bots)} muvaffaqiyatli ulandi: @{me.username} (Profil: '{profile.name}')"
            )
        except Exception as e:
            logger.error(f"❌ Bot #{idx + 1} tokeni bilan ulanishda xatolik: {e}")
            await bot.session.close()

    if not valid_bots:
        logger.error("Birorta ham bot muvaffaqiyatli ishga tushmadi!")
        sys.exit(1)

    logger.info(f"Jami {len(valid_bots)} ta alohida bot bir vaqtda parallel ishga tushirilmoqda...")

    # Start health check server
    web_runner = await start_web_server(bot_names)

    # Start periodic file cleanup task
    cleanup_task = asyncio.create_task(periodic_cleanup())

    # Small pause to allow any prior container to release long-polling cleanly
    await asyncio.sleep(2)

    try:
        # Start concurrent polling for all valid bot instances
        await dp.start_polling(
            *valid_bots,
            allowed_updates=dp.resolve_used_update_types(),
            handle_signals=True
        )
    finally:
        cleanup_task.cancel()
        await web_runner.cleanup()
        await close_http_session()
        for b in valid_bots:
            try:
                await b.session.close()
            except Exception:
                pass
        logger.info("Barcha botlar to'xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Botlar to'xtatildi.")
