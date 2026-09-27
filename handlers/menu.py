import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

from constants import IMAGE_BUTTON, LOADING_TEXT, SENDING_IMAGE_ERROR_TEXT, TEXT_BUTTON, URL
from exceptions import BotError
from utils.recognition import TextRecognizer
from utils.scraper import ImageScraper

router = Router()
logger = logging.getLogger(__name__)


async def answer_error(message: Message, error: Exception, error_text: str) -> None:
    """Log the error and show the error text to the user.

    Args:
        message: Incoming message that caused the error.
        error: Raised exception.
        error_text: Text shown to the user.
    """
    logger.error("Request %r of user %s failed: %r", message.text, message.from_user.id, error)
    await message.answer(error_text)


@router.message(F.text == TEXT_BUTTON)
async def send_text(
    message: Message,
    bot: Bot,
    scraper: ImageScraper,
    recognizer: TextRecognizer,
) -> None:
    """Send the text recognized from the target image, or an error message on failure.

    Args:
        message: Incoming message with the text button label.
        bot: Bot instance injected by aiogram.
        scraper: Image URL scraper injected by Dispatcher.
        recognizer: Text recognizer injected by Dispatcher.
    """
    logger.info("User %s requested text", message.from_user.id)
    info_message = await bot.send_message(message.from_user.id, LOADING_TEXT)
    try:
        img_url = await scraper.get_img_url(URL)
        text = await recognizer.recognize_text(img_url)
    except BotError as error:
        await answer_error(message, error, error.user_message)
        return
    finally:
        await bot.delete_message(message.from_user.id, info_message.message_id)
    await message.answer(text)
    logger.info("Text sent to user %s", message.from_user.id)


@router.message(F.text == IMAGE_BUTTON)
async def send_img(message: Message, bot: Bot, scraper: ImageScraper) -> None:
    """Send the target image, or an error message on failure.

    Args:
        message: Incoming message with the image button label.
        bot: Bot instance injected by aiogram.
        scraper: Image URL scraper injected by Dispatcher.
    """
    logger.info("User %s requested image", message.from_user.id)
    try:
        img_url = await scraper.get_img_url(URL)
        # Telegram downloads the image by URL itself and fails if it can't.
        await bot.send_photo(message.chat.id, img_url)
    except BotError as error:
        await answer_error(message, error, error.user_message)
        return
    except TelegramBadRequest as error:
        await answer_error(message, error, SENDING_IMAGE_ERROR_TEXT)
        return
    logger.info("Image sent to user %s", message.from_user.id)
