# Revolt imports
import revolt
from revolt.ext import commands

# Built-in imports
import os

# Custom imports
from utils.client import Client

# Aiohttp imports
from aiohttp_client_cache import CachedSession  # type: ignore

# Utility imports
from utils.dman import get


class apod(commands.Cog):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    @commands.command(name="apod", usage="Get the Astronomy Picture of the Day")
    async def apod(self, ctx: commands.Context):
        """Get the Astronomy Picture of the Day"""

        async with CachedSession(cache=self.client.cache) as session:

            msg = await ctx.message.reply(
                embeds=[
                    revolt.SendableEmbed(
                        title="Fetching data...",
                        description="This may take a second if data isn't cached.",
                    )
                ]
            )

            resp = await session.get(
                "https://api.nasa.gov/planetary/apod",
                params={"api_key": os.getenv("NASA_TOKEN")},
            )
            resp.raise_for_status()
            data = await resp.json()

            await msg.edit(
                embeds=[
                    revolt.SendableEmbed(
                        title="Uploading image...",
                        description="Revolt may take a second to process the image, please be patient while it uploads.",
                    )
                ]
            )

            await msg.edit(
                embeds=[
                    revolt.SendableEmbed(
                        title="APOD: " + data["title"],
                        description=data["explanation"]
                        + "\n\n**Copyright:**\n"
                        + data["copyright"].removeprefix("\n"),
                        media=await get(
                            self.client, self.client.imagesCache, data["url"]
                        ),
                    )
                ]
            )


def setup(client: Client):
    client.add_cog(apod(client))  # type: ignore
