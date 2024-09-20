# Revolt imports
from datetime import datetime
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


class epic(commands.Cog):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    @commands.command(name="epic", usage="View recent images from NASA's EPIC camera")
    async def epic(self, ctx: commands.Context, *, angle: commands.IntConverter = 1):

        if angle > 9 or angle < 1:
            await ctx.message.reply(
                embeds=[
                    revolt.SendableEmbed(
                        title="Invalid input",
                        description="There's only 9 epic angles, select from `1` to `9`.",
                    )
                ]
            )
            return

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
                "https://api.nasa.gov/EPIC/api/natural/images",
                params={"api_key": os.getenv("NASA_TOKEN")},
            )
            resp.raise_for_status()
            data = await resp.json()
            date = datetime.strptime(data[angle - 1]["date"], "%Y-%m-%d %H:%M:%S")

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
                        title="Earth Polychromatic Imaging Camera",
                        description="Taken on: "
                        + date.strftime("%d/%m/%Y"),  # Human readable day/month/year
                        media=await get(
                            self.client,
                            self.client.imagesCache,
                            "https://epic.gsfc.nasa.gov/archive/natural/{}/{:02}/{:02}/png/{}.png".format(
                                date.year,
                                date.month,
                                date.day,
                                data[angle - 1]["image"],
                            ),
                        ),
                    )
                ]
            )


def setup(client: Client):
    client.add_cog(epic(client))  # type: ignore
