import io
import re

import pytest
from aiohttp import ClientConnectionError
from PIL import Image

from exceptions import BotConnectionError, BotRecognizingError
from tests.fakes import FakeOCR, FakeSession
from utils.recognition import TesseractOCR, TextRecognizer

IMG_URL = "http://example.com/schedule.png"
DOWNLOAD_ERROR = re.escape(f"Failed to download {IMG_URL}")


def make_png() -> bytes:
    """Create a tiny PNG image in memory."""
    buffer = io.BytesIO()
    Image.new("RGB", (1, 1)).save(buffer, format="PNG")
    return buffer.getvalue()


def make_recognizer(ocr: FakeOCR, content: bytes) -> TextRecognizer:
    """Create a recognizer whose session serves the content by ``IMG_URL``."""
    session = FakeSession()
    session.add_response(IMG_URL, content=content)
    return TextRecognizer(session, ocr=ocr)


async def test_recognize_text_returns_ocr_text() -> None:
    recognizer = make_recognizer(FakeOCR("Расписание"), make_png())

    assert await recognizer.recognize_text(IMG_URL) == "Расписание"


@pytest.mark.parametrize("ocr_text", ["", "   \n\t"])
async def test_recognize_text_raises_when_no_text(ocr_text: str) -> None:
    recognizer = make_recognizer(FakeOCR(ocr_text), make_png())

    with pytest.raises(BotRecognizingError, match=re.escape(f"No text recognized from {IMG_URL}")):
        await recognizer.recognize_text(IMG_URL)


@pytest.mark.parametrize("content", [b"", b"not an image"])
async def test_recognize_text_raises_when_data_is_not_image(content: bytes) -> None:
    recognizer = make_recognizer(FakeOCR("text"), content)

    with pytest.raises(BotRecognizingError, match=re.escape(f"Failed to open image {IMG_URL}")):
        await recognizer.recognize_text(IMG_URL)


async def test_recognize_text_propagates_ocr_error() -> None:
    recognizer = make_recognizer(FakeOCR(fail=True), make_png())

    with pytest.raises(BotRecognizingError, match="Fake OCR failed"):
        await recognizer.recognize_text(IMG_URL)


async def test_recognize_text_raises_on_network_error() -> None:
    session = FakeSession()
    session.add_error(IMG_URL, ClientConnectionError("refused"))
    recognizer = TextRecognizer(session, ocr=FakeOCR("text"))

    with pytest.raises(BotConnectionError, match=DOWNLOAD_ERROR):
        await recognizer.recognize_text(IMG_URL)


async def test_recognize_text_raises_on_missing_image() -> None:
    recognizer = TextRecognizer(FakeSession(), ocr=FakeOCR("text"))

    with pytest.raises(BotConnectionError, match=DOWNLOAD_ERROR):
        await recognizer.recognize_text(IMG_URL)


def test_text_recognizer_uses_tesseract_by_default() -> None:
    assert isinstance(TextRecognizer(FakeSession()).ocr, TesseractOCR)
