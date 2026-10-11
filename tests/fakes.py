import socket
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from types import TracebackType
from typing import Any

from aiogram import Bot
from aiogram.client.session.base import BaseSession
from aiogram.methods import SendMessage, SendPhoto, TelegramMethod
from aiogram.types import Chat, Message
from aiohttp import ClientResponseError, RequestInfo
from aiohttp.abc import AbstractResolver, ResolveResult
from multidict import CIMultiDict, CIMultiDictProxy
from PIL import Image
from yarl import URL

from exceptions import BotRecognizingError


class FakeResponse:
    """Fake aiohttp response with in-memory content, status and an optional request error.

    Args:
        url: URL of the requested resource.
        content: Body of the response.
        status: HTTP status of the response.
        error: Exception raised when the request is sent, like a network error.
    """

    def __init__(
        self,
        url: str,
        content: bytes = b"",
        status: int = 200,
        error: BaseException | None = None,
    ) -> None:
        self.url = url
        self.content = content
        self.status = status
        self.error = error

    async def __aenter__(self) -> "FakeResponse":
        if self.error is not None:
            raise self.error
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None

    def raise_for_status(self) -> None:
        """Raise ``ClientResponseError`` if the status is not successful, like aiohttp does."""
        if self.status >= 400:
            request_info = RequestInfo(URL(self.url), "GET", CIMultiDictProxy(CIMultiDict()))
            raise ClientResponseError(request_info, (), status=self.status, message="Fake error")

    async def read(self) -> bytes:
        """Return the response body."""
        return self.content


class FakeSession:
    """Fake aiohttp session serving in-memory responses by URL.

    Unknown URLs are answered with the 404 status.
    """

    def __init__(self) -> None:
        self.responses: dict[str, FakeResponse] = {}

    def add_response(self, url: str, content: bytes = b"", status: int = 200) -> None:
        """Store a response for the URL."""
        self.responses[url] = FakeResponse(url, content=content, status=status)

    def add_error(self, url: str, error: BaseException) -> None:
        """Make the request to the URL fail with the error."""
        self.responses[url] = FakeResponse(url, error=error)

    def get(self, url: str) -> FakeResponse:
        """Return the stored response for the URL."""
        return self.responses.get(url, FakeResponse(url, status=404))


class FakeOCR:
    """Fake OCR engine returning the stored text.

    Args:
        text: Text returned for any image.
        fail: Raise ``BotRecognizingError`` instead of returning the text.
    """

    def __init__(self, text: str = "", fail: bool = False) -> None:
        self.text = text
        self.fail = fail

    def image_to_text(self, image: Image.Image) -> str:
        """Return the stored text or raise ``BotRecognizingError``."""
        if self.fail:
            raise BotRecognizingError("Fake OCR failed")
        return self.text


@dataclass
class FakeUser:
    """Fake Telegram user with only the ID."""

    id: int


@dataclass
class FakeChat:
    """Fake Telegram chat with only the ID."""

    id: int


@dataclass
class FakeMessage:
    """Fake Telegram message storing the answers in memory.

    Args:
        text: Text of the incoming message.
        user_id: ID of the user and the private chat the message came from.
    """

    text: str | None = None
    user_id: int = 1
    message_id: int = 1
    answers: list[tuple[str, Any]] = field(default_factory=list)

    @property
    def from_user(self) -> FakeUser:
        """Return the message sender."""
        return FakeUser(self.user_id)

    @property
    def chat(self) -> FakeChat:
        """Return the private chat with the sender."""
        return FakeChat(self.user_id)

    async def answer(self, text: str, reply_markup: Any = None) -> "FakeMessage":
        """Store the answer text with its keyboard."""
        self.answers.append((text, reply_markup))
        return FakeMessage(text=text, user_id=self.user_id)


class FakeBot:
    """Fake aiogram bot storing sent and deleted messages in memory.

    Args:
        photo_error: Exception raised when a photo is sent, like ``TelegramBadRequest``.
    """

    def __init__(self, photo_error: BaseException | None = None) -> None:
        self.photo_error = photo_error
        self.sent_messages: list[tuple[int, str, int]] = []
        self.deleted_messages: list[tuple[int, int]] = []
        self.sent_photos: list[tuple[int, str]] = []

    async def send_message(self, chat_id: int, text: str) -> FakeMessage:
        """Store the message and return it with a new message ID."""
        message_id = len(self.sent_messages) + 100
        self.sent_messages.append((chat_id, text, message_id))
        return FakeMessage(text=text, user_id=chat_id, message_id=message_id)

    async def delete_message(self, chat_id: int, message_id: int) -> bool:
        """Store the deleted message ID."""
        self.deleted_messages.append((chat_id, message_id))
        return True

    async def send_photo(self, chat_id: int, photo: str) -> None:
        """Store the photo URL or raise the stored error."""
        if self.photo_error is not None:
            raise self.photo_error
        self.sent_photos.append((chat_id, photo))


class FakeScraper:
    """Fake image scraper returning the stored image URL.

    Args:
        img_url: Image URL returned for any web page.
        error: Exception raised instead of returning the URL.
    """

    def __init__(self, img_url: str = "", error: BaseException | None = None) -> None:
        self.img_url = img_url
        self.error = error
        self.requested_urls: list[str] = []

    async def get_img_url(self, url: str) -> str:
        """Store the requested URL and return the image URL or raise the stored error."""
        self.requested_urls.append(url)
        if self.error is not None:
            raise self.error
        return self.img_url


class FakeRecognizer:
    """Fake text recognizer returning the stored text.

    Args:
        text: Text returned for any image.
        error: Exception raised instead of returning the text.
    """

    def __init__(self, text: str = "", error: BaseException | None = None) -> None:
        self.text = text
        self.error = error
        self.requested_urls: list[str] = []

    async def recognize_text(self, img_url: str) -> str:
        """Store the image URL and return the text or raise the stored error."""
        self.requested_urls.append(img_url)
        if self.error is not None:
            raise self.error
        return self.text


class FakeTelegramSession(BaseSession):
    """Fake aiogram session storing Telegram API requests in memory instead of sending them.

    Sent messages and photos are answered with a new ``Message``, other methods with ``True``.
    """

    def __init__(self) -> None:
        super().__init__()
        self.requests: list[TelegramMethod[Any]] = []
        self.errors: dict[type[TelegramMethod[Any]], BaseException] = {}

    def add_error(self, method_type: type[TelegramMethod[Any]], error: BaseException) -> None:
        """Make requests of the method type fail with the error, like ``TelegramBadRequest``."""
        self.errors[method_type] = error

    def get_requests(self, method_type: type[TelegramMethod[Any]]) -> list[Any]:
        """Return the stored requests of the method type in order."""
        return [request for request in self.requests if isinstance(request, method_type)]

    async def make_request(
        self,
        bot: Bot,
        method: TelegramMethod[Any],
        timeout: int | None = None,
    ) -> Any:
        """Store the request and return a fake result or raise the stored error."""
        self.requests.append(method)
        error = self.errors.get(type(method))
        if error is not None:
            raise error
        if isinstance(method, SendMessage | SendPhoto):
            chat = Chat(id=method.chat_id, type="private")
            return Message(message_id=len(self.requests), date=datetime.now(), chat=chat)
        return True

    async def stream_content(
        self,
        url: str,
        headers: dict[str, Any] | None = None,
        timeout: int = 30,
        chunk_size: int = 65536,
        raise_for_status: bool = True,
    ) -> AsyncGenerator[bytes]:
        """Yield no content, the bot doesn't download files."""
        yield b""

    async def close(self) -> None:
        """Do nothing, there is no connection to close."""


class FakeResolver(AbstractResolver):
    """Fake aiohttp DNS resolver pointing every host to the local server port.

    Args:
        port: Port of the local server.
    """

    def __init__(self, port: int) -> None:
        self.port = port
        self.resolved_hosts: list[str] = []

    async def resolve(
        self,
        host: str,
        port: int = 0,
        family: socket.AddressFamily = socket.AF_INET,
    ) -> list[ResolveResult]:
        """Store the host and resolve it to the local server."""
        self.resolved_hosts.append(host)
        return [
            ResolveResult(
                hostname=host,
                host="127.0.0.1",
                port=self.port,
                family=socket.AF_INET,
                proto=0,
                flags=socket.AI_NUMERICHOST,
            )
        ]

    async def close(self) -> None:
        """Do nothing, there is nothing to release."""
