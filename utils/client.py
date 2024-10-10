# Revolt imports
import revolt
from revolt.ext import commands

# Utility imports
import logging
from aiohttp_client_cache import SQLiteBackend
from utils.errorHandler import errorHandler


class Client(commands.CommandsClient):
    def __init__(
        self,
        *args,
        logger: logging.Logger = logging.getLogger("Spacey"),
        case_insensitive: bool = False,
        **kwargs,
    ):
        super().__init__(
            *args,
            help_command=None,
            case_insensitive=case_insensitive,
            **kwargs,
        )

        self.logger = logger

        self.cache = SQLiteBackend(
            cache_name="./.cache/requests.sqlite",
            expire_after=60 * 60,
            allowed_codes=[200],
            allowed_methods=["GET", "POST"],
            timeout=2.5,
        )

        self.imagesCache = SQLiteBackend(
            cache_name="./.cache/images.sqlite",
            expire_after=2 * 60 * 60,
            allowed_codes=[200],
            allowed_methods=["GET", "POST"],
            timeout=2.5,
        )

        self.hasInitialized = False

    async def get_prefix(self, message: revolt.Message) -> str | list[str]:
        return [
            "/s ",
            self.user.mention,
            "s!",
        ]

    async def on_ready(self):
        self.logger.info(
            f"Logged in as {self.user.name}"
            if self.hasInitialized == False
            else f"Reconnected as {self.user.name}"
        )

        await self.edit_status(
            presence=revolt.PresenceType.online, text="Watching the stars! 🌠"
        )

        self.hasInitialized = True

    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        await errorHandler(ctx, error)

        self.logger.error("An error occurred", exc_info=True)
