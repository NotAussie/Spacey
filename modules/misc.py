# Revolt imports
import revolt
from revolt.ext import commands

# Custom imports
from utils.client import Client

# Built-in imports
import time


class misc(commands.Cog):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    @commands.command(name="ping", usage="Ping the bot")
    async def ping(self, ctx: commands.Context):
        """Ping the bot"""

        startTime = time.time()
        msg = await ctx.message.reply(embeds=[revolt.SendableEmbed(title="Pinging!")])
        endTime = time.time()

        await msg.edit(
            embeds=[
                revolt.SendableEmbed(
                    title="Pong!",
                    description=f"Pong! (Roundtrip: {endTime - startTime:.2f} seconds)",
                )
            ]
        )


def load_module(client: Client):
    client.add_cog(misc(client))  # type: ignore
