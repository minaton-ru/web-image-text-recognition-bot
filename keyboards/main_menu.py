from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from constants import IMAGE_BUTTON, TEXT_BUTTON

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=TEXT_BUTTON), KeyboardButton(text=IMAGE_BUTTON)]],
    resize_keyboard=True,
)
