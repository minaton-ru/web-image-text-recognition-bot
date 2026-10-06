import pytest

from constants import WELCOME_TEXT
from handlers.start import command_start
from keyboards.main_menu import MAIN_MENU
from tests.fakes import FakeMessage


async def test_command_start_answers_welcome_text_with_main_menu() -> None:
    message = FakeMessage(text="/start")

    await command_start(message)

    assert message.answers == [(WELCOME_TEXT, MAIN_MENU)]


@pytest.mark.parametrize("text", ["", None, "   ", "/start payload"])
async def test_command_start_ignores_message_text(text: str | None) -> None:
    message = FakeMessage(text=text)

    await command_start(message)

    assert message.answers == [(WELCOME_TEXT, MAIN_MENU)]
