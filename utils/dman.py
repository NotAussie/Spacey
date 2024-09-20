# Revolt imports
import revolt


# Utility imports
from .client import Client

# AIOHTTP imports
from aiohttp_client_cache import CacheBackend, CachedSession  # type: ignore

# Built-in imports
import logging

# Type imports
from typing import Literal

logger = logging.getLogger("Spacey")


async def get(
    client: Client,
    cache: CacheBackend,
    url: str,
    tag: Literal[
        "attachments",
        "avatars",
        "backgrounds",
        "icons",
        "banners",
        "emojis",
    ] = "attachments",
    params: dict[str, str] | None = None,
) -> str:
    """Fetches the inputted image and uploads the image to Revolt, using local caching.

    This wraps AIOHTTP Cache to provide a simple function for caching images.
    """

    async with CachedSession(cache=cache) as session:
        resp = await session.get(url, params=params)
        resp.raise_for_status()

        # Check the content type
        mime = resp.headers["Content-Type"]
        if not mime.startswith(("image/", "video/", "text/", "audio/", "application/")):
            raise ValueError("Invalid content type")

        # Read the image data
        imageData = await resp.read()

        # Upload the file to Revolt
        try:
            ulid = await client.upload_file(revolt.File(imageData), tag=tag)
        except (revolt.errors.Forbidden, revolt.errors.AutumnDisabled):
            logger.error("Failed to upload image to Revolt")

        return ulid.id
