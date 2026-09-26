import logging

from aiogram import Bot, F, Router
from aiogram.types import Message

from constants import IMAGE_BUTTON, LOADING_TEXT, TEXT_BUTTON, URL
from utils.recognition import TextRecognizer
from utils.scraper import ImageScraper

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == TEXT_BUTTON)
async def send_text(
    message: Message,
    bot: Bot,
    scraper: ImageScraper,
    recognizer: TextRecognizer,
) -> None:
    """Send the text recognized from the target image.

    Args:
        message: Incoming message with the text button label.
        bot: Bot instance injected by aiogram.
        scraper: Image URL scraper injected by Dispatcher.
        recognizer: Text recognizer injected by Dispatcher.
    """
    logger.info("User %s requested text", message.from_user.id)
    info_message = await bot.send_message(message.from_user.id, LOADING_TEXT)
    img_url = await scraper.get_img_url(URL)
    text = await recognizer.recognize_text(img_url)
    await bot.delete_message(message.from_user.id, info_message.message_id)
    await message.answer(text)
    logger.info("Text sent to user %s", message.from_user.id)


@router.message(F.text == IMAGE_BUTTON)
async def send_img(message: Message, bot: Bot, scraper: ImageScraper) -> None:
    """Send the target image.

    Args:
        message: Incoming message with the image button label.
        bot: Bot instance injected by aiogram.
        scraper: Image URL scraper injected by Dispatcher.
    """
    logger.info("User %s requested image", message.from_user.id)
    img_url = await scraper.get_img_url(URL)
    await bot.send_photo(message.chat.id, img_url)
