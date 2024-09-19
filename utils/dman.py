# Download helper for Revolt (DMman: Download manager)
# This file will be rewritten in the future to help with readability and maintainability

# Revolt imports
import revolt

# Utility imports
import aiohttp
from utils.client import Client
import aiofiles
from utils.randomstring import randomword

# Built-in imports
import logging
from datetime import datetime, timedelta
import time
import os
import json
from urllib.parse import urlparse

logger = logging.getLogger("Spacey")

# Ensure images.json exists
if not os.path.exists(os.path.join(os.getcwd(), ".cache", "images.json")):
    with open(os.path.join(os.getcwd(), ".cache", "images.json"), "w") as f:
        f.write("{}")


def removeQueryParams(url: str) -> str:
    """Removes query parameters from the URL."""
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"


async def purgeExpired():
    """Purges expired images from the local cache."""
    if not os.path.exists(os.path.join(os.getcwd(), ".cache", "images")):
        os.makedirs(os.path.join(os.getcwd(), ".cache", "images"))

    async with aiofiles.open(
        os.path.join(os.getcwd(), ".cache", "images.json"), mode="r"
    ) as rawDataBase:
        database = json.loads(await rawDataBase.read())
        for url in database:
            expirydata = datetime.fromtimestamp(database[url]["expire"])
            if expirydata <= datetime.now():
                os.remove(
                    os.path.join(os.getcwd(), ".cache", "images", database[url]["file"])
                )
                del database[url]

        async with aiofiles.open(
            os.path.join(os.getcwd(), ".cache", "images.json"), mode="w"
        ) as rawDataBase:
            await rawDataBase.write(json.dumps(database))


async def getLocal(url: str) -> bytes | None:
    """Gets a file from the local cache and returns the bytes."""
    baseUrl = removeQueryParams(url)

    if not os.path.exists(os.path.join(os.getcwd(), ".cache", "images")):
        os.makedirs(os.path.join(os.getcwd(), ".cache", "images"))

    async with aiofiles.open(
        os.path.join(os.getcwd(), ".cache", "images.json"), mode="r"
    ) as rawDataBase:
        database = json.loads(await rawDataBase.read())

        if baseUrl in database:
            expirydata = datetime.fromtimestamp(database[baseUrl]["expire"])

            # Check if the cached data has expired
            if expirydata <= datetime.now():
                # If expired, delete the cached file and entry
                os.remove(
                    os.path.join(
                        os.getcwd(), ".cache", "images", database[baseUrl]["file"]
                    )
                )
                logger.info(f"Cache expired for URL: {baseUrl}. Deleted cached file.")
                del database[baseUrl]

                async with aiofiles.open(
                    os.path.join(os.getcwd(), ".cache", "images.json"), mode="w"
                ) as rawDataBase:
                    await rawDataBase.write(json.dumps(database))

                return None

            # If not expired, return the cached image
            async with aiofiles.open(
                os.path.join(
                    os.getcwd(), ".cache", "images", database[baseUrl]["file"]
                ),
                mode="rb",  # Open in binary mode
            ) as image:
                logger.info(f"Retrieved cached image for URL: {baseUrl}")
                return await image.read()

        logger.info(f"No cached image found for URL: {baseUrl}")
        return None


async def saveLocal(
    url: str, contentType: str, data: bytes, expiryDelta: timedelta | None = None
) -> None:
    """Saves a file to the local cache."""
    baseUrl = removeQueryParams(url)

    if not os.path.exists(os.path.join(os.getcwd(), ".cache", "images")):
        os.makedirs(os.path.join(os.getcwd(), ".cache", "images"))

    async with aiofiles.open(
        os.path.join(os.getcwd(), ".cache", "images.json"), mode="r"
    ) as rawDataBase:
        database = json.loads(await rawDataBase.read())
        if not expiryDelta is None:
            expiryData = datetime.now() + expiryDelta
        else:
            expiryData = datetime.now() + timedelta(days=1)

        database[baseUrl] = {
            "file": randomword(10) + "." + contentType.split("/")[1],
            "expire": expiryData.timestamp(),
        }

        async with aiofiles.open(
            os.path.join(os.getcwd(), ".cache", "images.json"), mode="w"
        ) as rawDataBase:
            await rawDataBase.write(json.dumps(database))

    async with aiofiles.open(
        os.path.join(os.getcwd(), ".cache", "images", database[baseUrl]["file"]),
        mode="wb",
    ) as image:
        await image.write(data)

    logger.info(f"Saved image to cache for URL: {baseUrl}. Expires at: {expiryData}.")


async def get(client: Client, url: str) -> str:
    """Fetches the inputted image and uploads the image to Revolt, using local caching."""

    # Attempt to get the image from local cache
    cachedData = await getLocal(url)
    if cachedData is not None:
        # If we have cached data, upload it to Revolt
        uploadStartTime = time.time()
        ulid: revolt.utils.Ulid = await client.upload_file(
            revolt.File(cachedData), tag="attachments"
        )
        uploadEndTime = time.time()

        logger.info(
            f"Uploaded cached image from {url} in {uploadEndTime - uploadStartTime:.2f} seconds"
        )
        return ulid.id

    # If not cached, fetch the file using AioHttp
    async with aiohttp.ClientSession() as session:
        fetchStartTime = time.time()
        resp = await session.get(url)
        fetchEndTime = time.time()

        resp.raise_for_status()

        # Check the content type
        mime = resp.headers["Content-Type"]
        if not mime.startswith("image/"):
            raise ValueError("Invalid content type")

        # Read the image data
        imageData = await resp.read()

        # Save the image to local cache
        await saveLocal(url, mime, imageData)

        # Upload the file to Revolt
        uploadStartTime = time.time()
        ulid: revolt.utils.Ulid = await client.upload_file(
            revolt.File(imageData), tag="attachments"
        )
        uploadEndTime = time.time()

        logger.info(f"Fetched {url} in {fetchEndTime - fetchStartTime:.2f} seconds")
        logger.info(f"Uploaded {url} in {uploadEndTime - uploadStartTime:.2f} seconds")

        return ulid.id
