import re

import pytest
from aiohttp import ClientConnectionError, ClientResponseError

from exceptions import BotConnectionError
from tests.fakes import FakeSession
from utils.http import aiohttp_get_content

URL = "http://example.com/page"
DOWNLOAD_ERROR = re.escape(f"Failed to download {URL}")


async def test_aiohttp_get_content_returns_content() -> None:
    session = FakeSession()
    session.add_response(URL, content=b"<html></html>")

    assert await aiohttp_get_content(session, URL) == b"<html></html>"


async def test_aiohttp_get_content_returns_empty_content() -> None:
    session = FakeSession()
    session.add_response(URL, content=b"")

    assert await aiohttp_get_content(session, URL) == b""


@pytest.mark.parametrize("status", [404, 500])
async def test_aiohttp_get_content_raises_on_error_status(status: int) -> None:
    session = FakeSession()
    session.add_response(URL, content=b"error page", status=status)

    with pytest.raises(BotConnectionError, match=DOWNLOAD_ERROR) as error_info:
        await aiohttp_get_content(session, URL)
    assert isinstance(error_info.value.__cause__, ClientResponseError)


async def test_aiohttp_get_content_raises_on_missing_url() -> None:
    with pytest.raises(BotConnectionError, match=DOWNLOAD_ERROR):
        await aiohttp_get_content(FakeSession(), URL)


@pytest.mark.parametrize("error", [ClientConnectionError("refused"), TimeoutError()])
async def test_aiohttp_get_content_raises_on_network_error(error: Exception) -> None:
    session = FakeSession()
    session.add_error(URL, error)

    with pytest.raises(BotConnectionError, match=DOWNLOAD_ERROR) as error_info:
        await aiohttp_get_content(session, URL)
    assert error_info.value.__cause__ is error


async def test_aiohttp_get_content_does_not_hide_unexpected_error() -> None:
    session = FakeSession()
    session.add_error(URL, ValueError("bug"))

    with pytest.raises(ValueError):
        await aiohttp_get_content(session, URL)
