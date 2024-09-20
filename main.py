# Built-in imports
import asyncio
import os
from dotenv import load_dotenv
import logging
import importlib

# Miscellaneous imports
from rich.logging import RichHandler
from aiohttp import ClientSession

# Custom imports
from utils.client import Client

# Setup logging
logging.basicConfig(handlers=[RichHandler()], level=logging.DEBUG)
logger = logging.getLogger("Spacey")
logging.getLogger(name="aiosqlite").setLevel(logging.WARNING)
logging.getLogger(name="aiohttp_client_cache").setLevel(logging.WARNING)
logging.getLogger("revolt").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("charset_normalizer").setLevel(logging.WARNING)


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
                    logger.info(f"Loaded module {module_name}")
                except:
                    logger.error(f"Failed to load module {module_name}", exc_info=True)

        await asyncio.sleep(1)  # Wait for the modules to load
        await client.start()


asyncio.run(main())
