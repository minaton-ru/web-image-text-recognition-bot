import logging

import aiohttp
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


async def get_img_url(url: str) -> str:
    """Fetch the web page and extract the target image URL.

    Args:
        url: URL of the web page with the target image.
    Returns:
        Value of the image's ``src`` attribute.
    """
    async with aiohttp.ClientSession() as session, session.get(url) as response:
        html = await response.text()
    soup = BeautifulSoup(html, "html.parser")
    # The target image is inside a paragraph within the div with the "single" class.
    img_url = soup.find("div", class_="single").img.get("src")
    logger.debug("Image URL: %s", img_url)
    return img_url
