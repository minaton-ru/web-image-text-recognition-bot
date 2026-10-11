from datetime import datetime

import pytest
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import DeleteMessage, SendMessage, SendPhoto
from aiogram.types import Chat, Message, Update, User

from constants import (
    CONNECTION_ERROR_TEXT,
    IMAGE_BUTTON,
    LOADING_TEXT,
    PARSING_ERROR_TEXT,
    RECOGNIZING_ERROR_TEXT,
    SENDING_IMAGE_ERROR_TEXT,
    TEXT_BUTTON,
    WELCOME_TEXT,
)
from keyboards.main_menu import MAIN_MENU
from tests.fakes import FakeTelegramSession
from tests.integration.conftest import IMG_PATH, IMG_URL, PAGE_PATH, RECOGNIZED_TEXT, FakeSite

pytestmark = pytest.mark.integration

USER_ID = 42


def make_update(text: str) -> Update:
    """Create an update with a private message from ``USER_ID``."""
    message = Message(
        message_id=1,
        date=datetime.now(),
        chat=Chat(id=USER_ID, type="private"),
        from_user=User(id=USER_ID, is_bot=False, first_name="User"),
        text=text,
    )
    return Update(update_id=1, message=message)


def get_sent_texts(telegram_session: FakeTelegramSession) -> list[str]:
    """Return texts of the messages the bot sent."""
    return [request.text for request in telegram_session.get_requests(SendMessage)]


async def test_start_sends_welcome_with_main_menu(
    bot: Bot, dispatcher: Dispatcher, telegram_session: FakeTelegramSession
) -> None:
    await dispatcher.feed_update(bot, make_update("/start"))

    (request,) = telegram_session.get_requests(SendMessage)
    assert (request.chat_id, request.text) == (USER_ID, WELCOME_TEXT)
    assert request.reply_markup == MAIN_MENU


async def test_text_button_sends_recognized_text(
    bot: Bot, dispatcher: Dispatcher, telegram_session: FakeTelegramSession
) -> None:
    await dispatcher.feed_update(bot, make_update(TEXT_BUTTON))

    assert get_sent_texts(telegram_session) == [LOADING_TEXT, RECOGNIZED_TEXT]
    (delete_request,) = telegram_session.get_requests(DeleteMessage)
    assert delete_request.chat_id == USER_ID


async def test_image_button_sends_image_url_from_page(
    bot: Bot, dispatcher: Dispatcher, telegram_session: FakeTelegramSession
) -> None:
    await dispatcher.feed_update(bot, make_update(IMAGE_BUTTON))

    (request,) = telegram_session.get_requests(SendPhoto)
    assert (request.chat_id, request.photo) == (USER_ID, IMG_URL)
    assert get_sent_texts(telegram_session) == []


@pytest.mark.parametrize("button", [TEXT_BUTTON, IMAGE_BUTTON])
async def test_button_sends_connection_error_when_page_is_missing(
    bot: Bot,
    dispatcher: Dispatcher,
    telegram_session: FakeTelegramSession,
    site: FakeSite,
    button: str,
) -> None:
    site.remove_page(PAGE_PATH)

    await dispatcher.feed_update(bot, make_update(button))

    assert get_sent_texts(telegram_session)[-1] == CONNECTION_ERROR_TEXT


@pytest.mark.parametrize("html", [b"", b"   ", b"<html><body><p>No schedule</p></body></html>"])
async def test_text_button_sends_parsing_error_when_page_has_no_image(
    bot: Bot,
    dispatcher: Dispatcher,
    telegram_session: FakeTelegramSession,
    site: FakeSite,
    html: bytes,
) -> None:
    site.add_page(PAGE_PATH, html, "text/html")

    await dispatcher.feed_update(bot, make_update(TEXT_BUTTON))

    assert get_sent_texts(telegram_session) == [LOADING_TEXT, PARSING_ERROR_TEXT]


async def test_text_button_sends_connection_error_when_image_is_missing(
    bot: Bot, dispatcher: Dispatcher, telegram_session: FakeTelegramSession, site: FakeSite
) -> None:
    site.remove_page(IMG_PATH)

    await dispatcher.feed_update(bot, make_update(TEXT_BUTTON))

    assert get_sent_texts(telegram_session) == [LOADING_TEXT, CONNECTION_ERROR_TEXT]


async def test_text_button_sends_recognizing_error_when_image_is_broken(
    bot: Bot, dispatcher: Dispatcher, telegram_session: FakeTelegramSession, site: FakeSite
) -> None:
    site.add_page(IMG_PATH, b"not an image", "image/png")

    await dispatcher.feed_update(bot, make_update(TEXT_BUTTON))

    assert get_sent_texts(telegram_session) == [LOADING_TEXT, RECOGNIZING_ERROR_TEXT]


async def test_image_button_sends_error_when_telegram_rejects_photo(
    bot: Bot, dispatcher: Dispatcher, telegram_session: FakeTelegramSession
) -> None:
    method = SendPhoto(chat_id=USER_ID, photo=IMG_URL)
    error = TelegramBadRequest(method, "Bad Request: wrong file identifier")
    telegram_session.add_error(SendPhoto, error)

    await dispatcher.feed_update(bot, make_update(IMAGE_BUTTON))

    assert get_sent_texts(telegram_session) == [SENDING_IMAGE_ERROR_TEXT]


async def test_unknown_text_is_not_handled(
    bot: Bot, dispatcher: Dispatcher, telegram_session: FakeTelegramSession
) -> None:
    await dispatcher.feed_update(bot, make_update("hello"))

    assert telegram_session.requests == []
