import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TELEGRAM_BOT_TOKEN, LOGGING_LEVEL
from handlers import router
from database import initialize_db
from scheduler import setup_scheduler, job_processor

async def main():
    """The main function to initialize and run the bot."""
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, LOGGING_LEVEL.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Initialize the database
    await initialize_db()

    # Initialize the bot and dispatcher
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    # Include the command handlers router
    dp.include_router(router)
    
    # Start the scheduler
    setup_scheduler(bot)

    logger.info("Bot is starting...")
    # Start polling for updates from Telegram
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually.")