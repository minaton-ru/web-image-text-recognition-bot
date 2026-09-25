from aiogram import Bot, F, Router
from aiogram.types import Message

from constants import IMAGE_BUTTON, LOADING_TEXT, TEXT_BUTTON, URL
from utils.logger import logger
from utils.recognition import recognize_text
from utils.scraper import get_img_url

router = Router()


@router.message(F.text == TEXT_BUTTON)
async def send_text(message: Message, bot: Bot) -> None:
    """Send the text recognized from the schedule image.

    Args:
        message: Incoming message with the text button label.
        bot: Bot instance injected by aiogram.
    """
    logger.info("User %s requested text", message.from_user.id)
    info_message = await bot.send_message(message.from_user.id, LOADING_TEXT)
    img_url = await get_img_url(URL)
    text = await recognize_text(img_url)
    await bot.delete_message(message.from_user.id, info_message.message_id)
    await message.answer(text)
    logger.info("Text sent to user %s", message.from_user.id)


@router.message(F.text == IMAGE_BUTTON)
async def send_img(message: Message, bot: Bot) -> None:
    """Send the schedule image.

    Args:
        message: Incoming message with the image button label.
        bot: Bot instance injected by aiogram.
    """
    logger.info("User %s requested image", message.from_user.id)
    img_url = await get_img_url(URL)
    await bot.send_photo(message.chat.id, img_url)
