# Built-in imports
import asyncio
import os
from dotenv import load_dotenv
import logging

# Miscellaneous imports
from rich.logging import RichHandler
from logging.handlers import RotatingFileHandler
from aiohttp import ClientSession, ClientConnectionError

# Custom imports
from utils.client import Client

import logging
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler

# Configure the file handler
FileHandler = RotatingFileHandler(
    "logs/spacey.log", maxBytes=5 * 1024 * 1024, backupCount=5
)
FileHandler.setLevel(logging.DEBUG)
FileFormatter = logging.Formatter(
    "%(levelname)s:%(asctime)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
FileHandler.setFormatter(FileFormatter)

# Setup logging
logging.basicConfig(
    handlers=[
        RichHandler(),
        FileHandler,
    ],
    level=logging.DEBUG,
)

# Disable loggers
logging.getLogger(name="aiosqlite").setLevel(logging.WARNING)
logging.getLogger(name="aiohttp_client_cache").setLevel(logging.WARNING)
logging.getLogger("revolt").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("charset_normalizer").setLevel(logging.WARNING)

logger = logging.getLogger("Spacey")


async def main():
    load_dotenv()
    async with ClientSession() as session:
        client = Client(session, os.getenv("REVOLT_TOKEN"), logger=logger)

        # Automatically load each module via running the "setup" method in each module's file
        for module in os.listdir("./modules/"):
            if module.endswith(".py") and module != "__init__.py":
                module_name = module[:-3]
                logger.info(f"Loading module {module_name}")

                try:
                    client.load_extension(f"modules.{module_name}")
                    logger.info("Loaded module", module_name)
                except Exception:
                    logger.error("Failed to load module", module_name, exc_info=True)

        while True:
            try:
                await client.start()

            except ClientConnectionError:
                logger.error("Connection failed", exc_info=True)
                logger.info("Attempting to reconnect in 30 seconds...")
                await asyncio.sleep(30)

                try:
                    await client.start()
                except Exception:
                    logger.error("Failed to reconnect (shutting down)", exc_info=True)
                    break

            except KeyboardInterrupt:
                logger.info("Shutting down... (KeyboardInterrupt)")
                break


if __name__ == "__main__":
    logger.info("Starting Spacey...")
    asyncio.run(main())
