import logging

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from exceptions import BotParsingError
from utils.http import aiohttp_get_content

logger = logging.getLogger(__name__)


class ImageScraper:
    """Fetches a web page and extracts the target image URL from it.

    Args:
        session: Shared aiohttp session for HTTP requests.
    """

    def __init__(self, session: ClientSession) -> None:
        self.session = session

    async def fetch_html(self, url: str) -> bytes:
        """Download the web page HTML.

        Args:
            url: URL of the web page.
        Returns:
            Raw HTML of the web page, BeautifulSoup detects its encoding.
        Raises:
            BotConnectionError: If the web page can't be downloaded.
        """
        return await aiohttp_get_content(self.session, url)

    @staticmethod
    def parse_img_url(html: bytes | str) -> str:
        """Extract the target image URL from the web page HTML.

        Args:
            html: HTML of the web page with the target image.
        Returns:
            Value of the image's ``src`` attribute.
        Raises:
            BotParsingError: If the target image or its ``src`` attribute is not found.
        """
        soup = BeautifulSoup(html, "html.parser")
        # The target image is inside a paragraph within the div with the "single" class.
        div = soup.find("div", class_="single")
        img = div.img if div is not None else None
        img_url = img.get("src") if img is not None else None
        if not isinstance(img_url, str) or not img_url:
            raise BotParsingError("Target image URL is not found in the web page HTML")
        logger.debug("Image URL: %s", img_url)
        return img_url

    async def get_img_url(self, url: str) -> str:
        """Fetch the web page and extract the target image URL.

        Args:
            url: URL of the web page with the target image.
        Returns:
            Value of the image's ``src`` attribute.
        Raises:
            BotConnectionError: If the web page can't be downloaded.
            BotParsingError: If the target image URL is not found.
        """
        html = await self.fetch_html(url)
        return self.parse_img_url(html)
