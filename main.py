import asyncio

from aiogram import Bot, Dispatcher

from config import TOKEN
from handlers import menu, start
from utils.logger import logging
from constants import WELCOME_TEXT

logger = logging.getLogger(__name__)


async def main() -> None:
    """Create the bot, register routers and start polling."""
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_routers(start.router, menu.router)
    logger.info(f"Bot started {WELCOME_TEXT}")
    logger.info(f"Bot started {WELCOME_TEXT}")
    logger.info(f"Bot started {WELCOME_TEXT}")
    logger.info(f"Bot started {WELCOME_TEXT}")
    logger.info(f"Bot started {WELCOME_TEXT}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
