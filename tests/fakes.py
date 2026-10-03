from types import TracebackType

from aiohttp import ClientResponseError, RequestInfo
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
