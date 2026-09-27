import io
import logging

from aiohttp import ClientSession
from pytesseract import image_to_string, TesseractError, TesseractNotFoundError
from PIL import Image, UnidentifiedImageError

from constants import TESSERACT_CONFIG, TESSERACT_LANG
from exceptions import BotRecognizingError
from utils.http import aiohttp_get_content

logger = logging.getLogger(__name__)


class TextRecognizer:
    """Downloads an image and recognizes the text on it by pytesseract.

    Args:
        session: Shared aiohttp session for HTTP requests.
    """

    def __init__(self, session: ClientSession) -> None:
        self.session = session

    async def recognize_text(self, img_url: str) -> str:
        """Download the image and recognize the text on it by pytesseract.

        Args:
            img_url: URL of the image to recognize.
        Returns:
            Text recognized from the image.
        Raises:
            BotConnectionError: If the image can't be downloaded.
            BotRecognizingError: If the data is not an image, tesseract failed
                or no text was recognized.
        """
        data = await aiohttp_get_content(self.session, img_url)
        try:
            image = Image.open(io.BytesIO(data))
            text = image_to_string(image, lang=TESSERACT_LANG, config=TESSERACT_CONFIG)
        except (
            UnidentifiedImageError,
            TesseractError,
            TesseractNotFoundError,
        ) as error:
            raise BotRecognizingError(f"Failed to recognize {img_url}: {error!r}") from error
        if not text.strip():
            raise BotRecognizingError(f"No text recognized from {img_url}")
        logger.debug("Recognized %d characters from %s", len(text), img_url)
        return text
