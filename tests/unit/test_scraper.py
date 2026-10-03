import re

import pytest
from aiohttp import ClientConnectionError

from exceptions import BotConnectionError, BotParsingError
from tests.fakes import FakeSession
from utils.scraper import ImageScraper

PAGE_URL = "http://example.com/page"
IMG_URL = "http://example.com/schedule.jpg"
PAGE_HTML = f'<div class="single"><p><img src="{IMG_URL}"></p></div>'.encode()
DOWNLOAD_ERROR = re.escape(f"Failed to download {PAGE_URL}")
PARSING_ERROR = "Target image URL is not found in the web page HTML"


@pytest.mark.parametrize("html", [PAGE_HTML, PAGE_HTML.decode()])
def test_parse_img_url_returns_src(html: bytes | str) -> None:
    assert ImageScraper.parse_img_url(html) == IMG_URL


def test_parse_img_url_returns_first_image_of_target_div() -> None:
    html = (
        '<div class="other"><img src="other.jpg"></div>'
        '<div class="post single"><img src="first.jpg"><img src="second.jpg"></div>'
    )

    assert ImageScraper.parse_img_url(html) == "first.jpg"


@pytest.mark.parametrize(
    "html",
    [
        "",
        "   \n\t",
        "<html><body>No schedule</body></html>",
        '<div class="other"><img src="other.jpg"></div>',
        '<div class="single"><p>No image</p></div>',
        '<div class="single"><img alt="no src"></div>',
        '<div class="single"><img src=""></div>',
    ],
)
def test_parse_img_url_raises_when_image_url_not_found(html: str) -> None:
    with pytest.raises(BotParsingError, match=PARSING_ERROR):
        ImageScraper.parse_img_url(html)


def test_parse_img_url_rejects_none() -> None:
    with pytest.raises(TypeError):
        ImageScraper.parse_img_url(None)  # type: ignore[arg-type]


async def test_fetch_html_returns_page_content() -> None:
    session = FakeSession()
    session.add_response(PAGE_URL, content=PAGE_HTML)

    assert await ImageScraper(session).fetch_html(PAGE_URL) == PAGE_HTML


async def test_get_img_url_returns_image_url() -> None:
    session = FakeSession()
    session.add_response(PAGE_URL, content=PAGE_HTML)

    assert await ImageScraper(session).get_img_url(PAGE_URL) == IMG_URL


async def test_get_img_url_raises_on_network_error() -> None:
    session = FakeSession()
    session.add_error(PAGE_URL, ClientConnectionError("refused"))

    with pytest.raises(BotConnectionError, match=DOWNLOAD_ERROR):
        await ImageScraper(session).get_img_url(PAGE_URL)


async def test_get_img_url_raises_on_missing_page() -> None:
    with pytest.raises(BotConnectionError, match=DOWNLOAD_ERROR):
        await ImageScraper(FakeSession()).get_img_url(PAGE_URL)


async def test_get_img_url_raises_when_page_has_no_image() -> None:
    session = FakeSession()
    session.add_response(PAGE_URL, content=b"<html></html>")

    with pytest.raises(BotParsingError, match=PARSING_ERROR):
        await ImageScraper(session).get_img_url(PAGE_URL)
