import io
import logging
from typing import Protocol

from aiohttp import ClientSession
from PIL import Image, UnidentifiedImageError
from pytesseract import TesseractError, TesseractNotFoundError, image_to_string

from constants import TESSERACT_CONFIG, TESSERACT_LANG
from exceptions import BotRecognizingError
from utils.http import aiohttp_get_content

logger = logging.getLogger(__name__)


class OCREngine(Protocol):
    """Interface of an engine that recognizes text on an image."""

    def image_to_text(self, image: Image.Image) -> str:
        """Recognize the text on the image.

        Args:
            image: Image with the text.
        Returns:
            Text recognized from the image.
        Raises:
            BotRecognizingError: If the engine failed to recognize the text.
        """
        ...


class TesseractOCR:
    """Recognizes text on an image by pytesseract."""

    def image_to_text(self, image: Image.Image) -> str:
        """Recognize the text on the image by pytesseract.

        Args:
            image: Image with the text.
        Returns:
            Text recognized from the image.
        Raises:
            BotRecognizingError: If tesseract is not installed or failed to process the image.
        """
        try:
            return image_to_string(image, lang=TESSERACT_LANG, config=TESSERACT_CONFIG)
        except (TesseractError, TesseractNotFoundError) as error:
            logger.error("Tesseract failed: %r", error)
            raise BotRecognizingError(f"Tesseract failed: {error!r}") from error


class TextRecognizer:
    """Downloads an image and recognizes the text on it.

    Args:
        session: Shared aiohttp session for HTTP requests.
        ocr: Engine for text recognition, ``TesseractOCR`` by default.
    """

    def __init__(self, session: ClientSession, ocr: OCREngine | None = None) -> None:
        self.session = session
        self.ocr = ocr or TesseractOCR()

    async def recognize_text(self, img_url: str) -> str:
        """Download the image and recognize the text on it.

        Args:
            img_url: URL of the image to recognize.
        Returns:
            Text recognized from the image.
        Raises:
            BotConnectionError: If the image can't be downloaded.
            BotRecognizingError: If the data is not an image, OCR failed
                or no text was recognized.
        """
        data = await aiohttp_get_content(self.session, img_url)
        try:
            image = Image.open(io.BytesIO(data))
        except UnidentifiedImageError as error:
            logger.error("Failed to open image %s: %r", img_url, error)
            raise BotRecognizingError(f"Failed to open image {img_url}: {error!r}") from error
        text = self.ocr.image_to_text(image)
        if not text.strip():
            logger.error("No text recognized from %s", img_url)
            raise BotRecognizingError(f"No text recognized from {img_url}")
        logger.debug("Recognized %d characters from %s", len(text), img_url)
        return text
