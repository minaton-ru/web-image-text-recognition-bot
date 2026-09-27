import logging

from aiohttp import ClientError, ClientSession

from exceptions import BotConnectionError

logger = logging.getLogger(__name__)


async def aiohttp_get_content(session: ClientSession, url: str) -> bytes:
    """Download the resource content by URL.

    Args:
        session: Shared aiohttp session for HTTP requests.
        url: URL of the resource.
    Returns:
        Raw content of the resource.
    Raises:
        BotConnectionError: If the request failed or the response status is not successful.
    """
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.read()
    except (ClientError, TimeoutError) as error:
        raise BotConnectionError(f"Failed to download {url}: {error!r}") from error
    logger.debug("Downloaded %d bytes from %s", len(data), url)
    return data
