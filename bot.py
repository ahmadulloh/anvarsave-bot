import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers.user_handlers import user_router
from handlers.callback_handlers import callback_router
from services.downloader import cleanup_old_files

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("anvarsave_bot")

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

async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not defined in config or .env!")
        sys.exit(1)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Register routers
    dp.include_router(callback_router)
    dp.include_router(user_router)

    # Start periodic file cleanup task
    cleanup_task = asyncio.create_task(periodic_cleanup())

    # Drop pending updates to avoid backlog on startup
    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    logger.info(f"Bot @{me.username} successfully started!")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        cleanup_task.cancel()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
