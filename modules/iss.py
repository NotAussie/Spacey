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

logger = logging.getLogger("Spacey")


class spacepeeps(commands.Cog):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    @commands.command(
        name="iss",
        usage="View all the people on the ISS (and some infomation about the ISS)",
    )
    async def spacepeeps(self, ctx: commands.Context):
        """View all the people on the ISS (and some infomation about the ISS)"""

        async with CachedSession(cache=self.client.cache) as session:

            msg = await ctx.message.reply(
                embeds=[
                    revolt.SendableEmbed(
                        title="Fetching data...",
                        description="This may take a second if data isn't cached.",
                    )
                ],
                interactions=revolt.MessageInteractions(
                    reactions=["🚀", "👥"],
                    restrict_reactions=True,
                ),
            )

            resp = await session.get(
                "https://corquaid.github.io/international-space-station-APIs/JSON/people-in-space.json",
            )
            resp.raise_for_status()
            data = await resp.json()

            issSection = revolt.SendableEmbed(
                title="International Space Station",
                description=f"""People currently on the ISS
                
                **Total People on the ISS:**
                {data["number"]}

                **Expedition number:**
                {data["iss_expedition"]}

                *Click the buttons below to view different information about the ISS*
                """,
            )

            peopleText = ""
            for person in data["people"]:
                if person["iss"] != True:
                    continue

                peopleText = (
                    peopleText
                    + f"**{person['name']}**\nCountry: `{person['country']}`\nPosition: `{person['position']}`\n\n"
                )

            peopleSection = revolt.SendableEmbed(
                title="People on the ISS",
                description="People currently on the ISS"
                + "\n\n"
                + peopleText.removesuffix("\n\n"),
            )

            await msg.edit(embeds=[issSection])

            for _ in range(10):
                try:
                    _, _, emoji = await self.client.wait_for(
                        "reaction_add",
                        check=lambda message, member, emoji: member.id == ctx.author.id
                        and message.id == msg.id,
                        timeout=60,
                    )
                except asyncio.TimeoutError:
                    break

                if emoji == "🚀":
                    await msg.edit(embeds=[issSection])

                if emoji == "👥":
                    await msg.edit(embeds=[peopleSection])


def setup(client: Client):
    client.add_cog(spacepeeps(client))  # type: ignore
