import logging

import pytest
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import SendPhoto

from constants import ERROR_TEXT, LOADING_TEXT, SENDING_IMAGE_ERROR_TEXT, URL
from exceptions import BotConnectionError, BotError, BotParsingError, BotRecognizingError
from handlers.menu import answer_error, send_img, send_text
from tests.fakes import FakeBot, FakeMessage, FakeRecognizer, FakeScraper

USER_ID = 42
IMG_URL = "http://example.com/schedule.png"
BOT_ERRORS = [BotError, BotConnectionError, BotParsingError, BotRecognizingError]


def make_message(text: str | None = "button") -> FakeMessage:
    """Create an incoming message from ``USER_ID``."""
    return FakeMessage(text=text, user_id=USER_ID)


def make_bad_request() -> TelegramBadRequest:
    """Create the error Telegram returns when it can't download the photo."""
    method = SendPhoto(chat_id=USER_ID, photo=IMG_URL)
    return TelegramBadRequest(method, "Bad Request: wrong file identifier")


async def test_answer_error_answers_error_text() -> None:
    message = make_message()

    await answer_error(message, BotError("failed"), ERROR_TEXT)

    assert message.answers == [(ERROR_TEXT, None)]


async def test_answer_error_logs_error(caplog: pytest.LogCaptureFixture) -> None:
    message = make_message("Текст")

    with caplog.at_level(logging.ERROR, logger="handlers.menu"):
        await answer_error(message, BotError("failed"), ERROR_TEXT)

    assert f"Request 'Текст' of user {USER_ID} failed: BotError('failed')" in caplog.text


@pytest.mark.parametrize("text", ["", None, "   "])
async def test_answer_error_handles_empty_message_text(text: str | None) -> None:
    message = make_message(text)

    await answer_error(message, BotError("failed"), ERROR_TEXT)

    assert message.answers == [(ERROR_TEXT, None)]


async def test_send_text_answers_recognized_text() -> None:
    message, bot = make_message(), FakeBot()
    scraper, recognizer = FakeScraper(IMG_URL), FakeRecognizer("Расписание")

    await send_text(message, bot, scraper, recognizer)

    assert scraper.requested_urls == [URL]
    assert recognizer.requested_urls == [IMG_URL]
    assert message.answers == [("Расписание", None)]


async def test_send_text_deletes_loading_message() -> None:
    message, bot = make_message(), FakeBot()

    await send_text(message, bot, FakeScraper(IMG_URL), FakeRecognizer("text"))

    (chat_id, text, message_id), *_ = bot.sent_messages
    assert (chat_id, text) == (USER_ID, LOADING_TEXT)
    assert bot.deleted_messages == [(USER_ID, message_id)]


@pytest.mark.parametrize("error_class", BOT_ERRORS)
async def test_send_text_answers_error_when_scraper_fails(error_class: type[BotError]) -> None:
    message, bot = make_message(), FakeBot()
    recognizer = FakeRecognizer("text")

    await send_text(message, bot, FakeScraper(error=error_class("failed")), recognizer)

    assert recognizer.requested_urls == []
    assert message.answers == [(error_class.user_message, None)]
    assert len(bot.deleted_messages) == 1


@pytest.mark.parametrize("error_class", BOT_ERRORS)
async def test_send_text_answers_error_when_recognizer_fails(error_class: type[BotError]) -> None:
    message, bot = make_message(), FakeBot()
    recognizer = FakeRecognizer(error=error_class("failed"))

    await send_text(message, bot, FakeScraper(IMG_URL), recognizer)

    assert message.answers == [(error_class.user_message, None)]
    assert len(bot.deleted_messages) == 1


async def test_send_text_deletes_loading_message_on_unexpected_error() -> None:
    message, bot = make_message(), FakeBot()
    recognizer = FakeRecognizer(error=RuntimeError("unexpected"))

    with pytest.raises(RuntimeError, match="unexpected"):
        await send_text(message, bot, FakeScraper(IMG_URL), recognizer)

    assert message.answers == []
    assert len(bot.deleted_messages) == 1


async def test_send_img_sends_photo_to_chat() -> None:
    message, bot = make_message(), FakeBot()
    scraper = FakeScraper(IMG_URL)

    await send_img(message, bot, scraper)

    assert scraper.requested_urls == [URL]
    assert bot.sent_photos == [(USER_ID, IMG_URL)]
    assert message.answers == []


@pytest.mark.parametrize("error_class", BOT_ERRORS)
async def test_send_img_answers_error_when_scraper_fails(error_class: type[BotError]) -> None:
    message, bot = make_message(), FakeBot()

    await send_img(message, bot, FakeScraper(error=error_class("failed")))

    assert bot.sent_photos == []
    assert message.answers == [(error_class.user_message, None)]


async def test_send_img_answers_error_when_telegram_rejects_photo() -> None:
    message, bot = make_message(), FakeBot(photo_error=make_bad_request())

    await send_img(message, bot, FakeScraper(IMG_URL))

    assert message.answers == [(SENDING_IMAGE_ERROR_TEXT, None)]


async def test_send_img_propagates_unexpected_error() -> None:
    message, bot = make_message(), FakeBot(photo_error=RuntimeError("unexpected"))

    with pytest.raises(RuntimeError, match="unexpected"):
        await send_img(message, bot, FakeScraper(IMG_URL))

    assert message.answers == []
