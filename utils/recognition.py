import io

import aiohttp
import pytesseract
from PIL import Image

from constants import TESSERACT_CONFIG, TESSERACT_LANG
from utils.logger import logger


async def recognize_text(img_url: str) -> str:
    """Download the image and recognize the text on it.

    Args:
        img_url: URL of the image to recognize.

    Returns:
        Text recognized from the image.
    """
    async with aiohttp.ClientSession() as session, session.get(img_url) as response:
        data = await response.read()
    image = Image.open(io.BytesIO(data))
    text = pytesseract.image_to_string(image, lang=TESSERACT_LANG, config=TESSERACT_CONFIG)
    logger.debug("Recognized %d characters from %s", len(text), img_url)
    return text
