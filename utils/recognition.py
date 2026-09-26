import io
import logging

import aiohttp
import pytesseract
from PIL import Image

from constants import TESSERACT_CONFIG, TESSERACT_LANG

logger = logging.getLogger(__name__)


class TextRecognizer:
    """Downloads an image and recognizes the text on it by pytesseract.

    Args:
        session: Shared aiohttp session for HTTP requests.
    """

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def recognize_text(self, img_url: str) -> str:
        """Download the image and recognize the text on it by pytesseract.

        Args:
            img_url: URL of the image to recognize.
        Returns:
            Text recognized from the image.
        """
        async with self.session.get(img_url) as response:
            data = await response.read()
        image = Image.open(io.BytesIO(data))
        text = pytesseract.image_to_string(image, lang=TESSERACT_LANG, config=TESSERACT_CONFIG)
        logger.debug("Recognized %d characters from %s", len(text), img_url)
        return text
