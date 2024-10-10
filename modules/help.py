# Revolt imports
import revolt
from revolt.ext import commands

# Custom imports
from utils.client import Client

# Aiohttp imports
from aiohttp_client_cache import CachedSession  # type: ignore

# Built-in imports
import logging
import asyncio
import os

logger = logging.getLogger("Spacey")


class help(commands.Cog):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    @commands.command(
        name="help",
        usage="View all of Spacey's commands",
    )
    async def help(self, ctx: commands.Context):

        prefix = await self.client.get_prefix(ctx.message)

        embed = revolt.SendableEmbed(
            title="Spacey Help",
            description=f"""[[ Support ]]({os.getenv('SUPPORT_SERVER')}) [[ Invite ]]({os.getenv('INVITE_LINK')})
            
            **Astronomy Picture of the Day**
            `{prefix[0]}apod` - See the Astronomy Picture of the Day.

            **ISS**
            `{prefix[0]}iss` - View information about the International Space Station.

            **Earth Polychromatic Imaging Camera**
            `{prefix[0]}epic [angle]` - View the Earth's polychromatic imagery.

            `[]` *is an optional parameter*
            `()` *is a required parameter*
            """,
        )

        await ctx.message.reply(embeds=[embed])


def setup(client: Client):
    client.add_cog(help(client))  # type: ignore
