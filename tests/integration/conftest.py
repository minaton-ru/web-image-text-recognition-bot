from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from aiogram import Bot, Dispatcher
from aiohttp import ClientSession, TCPConnector, web
from aiohttp.test_utils import TestServer

from handlers import menu, start
from tests.fakes import FakeOCR, FakeResolver, FakeTelegramSession
from utils.recognition import TextRecognizer
from utils.scraper import ImageScraper

FIXTURES_DIR = Path(__file__).parent / "fixtures"
PAGE_PATH = "/raspisanie/"  # Path of the page from constants.URL
IMG_URL = "http://новоспасский-монастырь.рф/wp-content/uploads/schedule.png"  # From the HTML
IMG_PATH = "/wp-content/uploads/schedule.png"
RECOGNIZED_TEXT = "Расписание богослужений"
BOT_TOKEN = "42:TEST"


class FakeSite:
    """In-memory pages of the monastery site served by the fake web server.

    Unknown paths are answered with the 404 status.
    """

    def __init__(self) -> None:
        self.pages: dict[str, tuple[bytes, str]] = {}

    def add_page(self, path: str, content: bytes, content_type: str) -> None:
        """Store the page content served by the path."""
        self.pages[path] = (content, content_type)

    def remove_page(self, path: str) -> None:
        """Remove the page, so the path is answered with the 404 status."""
        self.pages.pop(path, None)

    async def handle(self, request: web.Request) -> web.Response:
        """Serve the stored page by the request path."""
        page = self.pages.get(request.path)
        if page is None:
            raise web.HTTPNotFound()
        content, content_type = page
        return web.Response(body=content, content_type=content_type)


def make_dispatcher(session: ClientSession, ocr: FakeOCR) -> Dispatcher:
    """Create the dispatcher with the routers and dependencies wired like in ``main.py``."""
    dp = Dispatcher(scraper=ImageScraper(session), recognizer=TextRecognizer(session, ocr=ocr))
    dp.include_routers(start.router, menu.router)
    return dp


@pytest.fixture(autouse=True)
def detach_routers() -> None:
    """Detach the module-level routers from the dispatcher of the previous test.

    aiogram allows attaching a router only once and has no public API to detach it.
    """
    for router in (start.router, menu.router):
        router._parent_router = None


@pytest.fixture
def site() -> FakeSite:
    """Create the site with the schedule page and image from the fixture files."""
    fake_site = FakeSite()
    fake_site.add_page(PAGE_PATH, (FIXTURES_DIR / "schedule.html").read_bytes(), "text/html")
    fake_site.add_page(IMG_PATH, (FIXTURES_DIR / "schedule.png").read_bytes(), "image/png")
    return fake_site


@pytest.fixture(autouse=True)
async def http_session(site: FakeSite) -> AsyncGenerator[ClientSession]:
    """Start a fresh fake web server and an HTTP session resolving every host to it."""
    app = web.Application()
    app.router.add_get("/{path:.*}", site.handle)
    server = TestServer(app)
    await server.start_server()
    connector = TCPConnector(resolver=FakeResolver(server.port))
    async with ClientSession(connector=connector) as session:
        yield session
    await server.close()


@pytest.fixture
def telegram_session() -> FakeTelegramSession:
    """Create the Telegram session storing requests in memory."""
    return FakeTelegramSession()


@pytest.fixture
def bot(telegram_session: FakeTelegramSession) -> Bot:
    """Create the bot sending requests to the fake Telegram session."""
    return Bot(token=BOT_TOKEN, session=telegram_session)


@pytest.fixture
def dispatcher(http_session: ClientSession) -> Dispatcher:
    """Create the dispatcher whose scraper and recognizer use the fake web server."""
    return make_dispatcher(http_session, FakeOCR(RECOGNIZED_TEXT))
