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
from utils.dman import purgeExpired

# Setup logging
logging.basicConfig(handlers=[RichHandler()], level=logging.DEBUG)
logger = logging.getLogger("Spacey")
logging.getLogger(name="aiosqlite").setLevel(logging.WARNING)
logging.getLogger(name="aiohttp_client_cache").setLevel(logging.WARNING)
logging.getLogger("revolt").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)


async def main():
    load_dotenv()
    async with ClientSession() as session:
        client = Client(session, os.getenv("REVOLT_TOKEN"), logger=logger)

        # Automatically load each module via running the "load_module" method in each module's file
        for module in os.listdir("./modules/"):
            if module.endswith(".py") and module != "__init__.py":
                module_name = module[:-3]
                logger.info(f"Loading module {module_name}")

                # Import the module and call the load_module function
                module = importlib.import_module(f"modules.{module_name}")
                if hasattr(module, "load_module"):
                    module.load_module(
                        client
                    )  # Call the load_module function with the client

        await purgeExpired()
        await client.start()


asyncio.run(main())
