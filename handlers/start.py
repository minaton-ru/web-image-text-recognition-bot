from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from constants import WELCOME_TEXT
from keyboards.main_menu import MAIN_MENU
from utils.logger import logger

router = Router()


@router.message(Command("start"))
async def command_start(message: Message) -> None:
    """Show the welcome message and the main menu keyboard.

    Args:
        message: Incoming /start message.
    """
    logger.info("User %s started the bot", message.from_user.id)
    await message.answer(WELCOME_TEXT, reply_markup=MAIN_MENU)
