import asyncio

import aiohttp
from aiogram import Bot, Dispatcher

from config import TOKEN
from handlers import menu, start
from utils.logger import logging
from utils.recognition import TextRecognizer
from utils.scraper import ImageScraper

logger = logging.getLogger(__name__)


async def main() -> None:
    """Create the bot, inject dependencies with a shared HTTP session and start polling."""
    bot = Bot(token=TOKEN)
    async with aiohttp.ClientSession() as session:
        dp = Dispatcher(scraper=ImageScraper(session), recognizer=TextRecognizer(session))
        dp.include_routers(start.router, menu.router)
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
