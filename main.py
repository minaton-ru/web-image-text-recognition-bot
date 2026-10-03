import asyncio

from aiogram import Bot, Dispatcher
from aiohttp import ClientSession, ClientTimeout

from config import TOKEN
from constants import HTTP_TIMEOUT
from handlers import menu, start
from utils.logger import logging
from utils.recognition import TextRecognizer
from utils.scraper import ImageScraper

logger = logging.getLogger(__name__)

timeout = ClientTimeout(total=HTTP_TIMEOUT)


async def main() -> None:
    """Create the bot, inject dependencies with a shared HTTP session and start polling."""
    bot = Bot(token=TOKEN)
    async with ClientSession(timeout=timeout) as session:
        dp = Dispatcher(scraper=ImageScraper(session), recognizer=TextRecognizer(session))
        dp.include_routers(start.router, menu.router)
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
