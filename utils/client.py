# Revolt imports
import revolt
from revolt.ext import commands

# Utility imports
from utils.detailedtrace import getDetailed
from rich import print
import logging

# Type imports
from typing_extensions import Self

from aiohttp_client_cache import SQLiteBackend


class Client(commands.CommandsClient):
    def __init__(
        self,
        *args,
        logger: logging.Logger = logging.getLogger("Spacey"),
        help_command: (
            commands.HelpCommand[Self] | None | revolt.utils._Missing
        ) = revolt.utils.Missing,
        case_insensitive: bool = False,
        **kwargs,
    ):
        super().__init__(
            *args,
            help_command=help_command,
            case_insensitive=case_insensitive,
            **kwargs,
        )

        self.logger = logger

        self.cache = SQLiteBackend(
            cache_name="./.cache/requests.db",
            expire_after=60 * 60,
            allowed_codes=[200],
            allowed_methods=["GET", "POST"],
            timeout=2.5,
        )

    async def get_prefix(self, message: revolt.Message) -> str | list[str]:
        return [self.user.mention, "s!", "/s"]

    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user.name}")

    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        self.logger.error("An error occurred!")
        print("[grey]" + getDetailed(error) + "[/grey]")
