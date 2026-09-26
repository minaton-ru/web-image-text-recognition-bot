import logging

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ImageScraper:
    """Fetches a web page and extracts the target image URL from it.

    Args:
        session: Shared aiohttp session for HTTP requests.
    """

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def fetch_html(self, url: str) -> str:
        """Download the web page HTML.

        Args:
            url: URL of the web page.
        Returns:
            HTML of the web page.
        """
        async with self.session.get(url) as response:
            html = await response.text()
        logger.debug("Fetched %d characters from %s", len(html), url)
        return html

    @staticmethod
    def parse_img_url(html: str) -> str:
        """Extract the target image URL from the web page HTML.

        Args:
            html: HTML of the web page with the target image.
        Returns:
            Value of the image's ``src`` attribute.
        """
        soup = BeautifulSoup(html, "html.parser")
        # The target image is inside a paragraph within the div with the "single" class.
        img_url = soup.find("div", class_="single").img.get("src")
        logger.debug("Image URL: %s", img_url)
        return img_url

    async def get_img_url(self, url: str) -> str:
        """Fetch the web page and extract the target image URL.

        Args:
            url: URL of the web page with the target image.
        Returns:
            Value of the image's ``src`` attribute.
        """
        html = await self.fetch_html(url)
        return self.parse_img_url(html)
