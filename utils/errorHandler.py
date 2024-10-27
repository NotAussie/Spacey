# Revolt imports
import revolt
from revolt.ext import commands

# View imports
from views import error


async def errorHandler(ctx: commands.Context, e: Exception):
    if isinstance(e, commands.CommandNotFound):

        await ctx.message.reply(embeds=[error("The entered command does not exist.")])

    elif isinstance(e, commands.errors.CommandOnCooldown):

        await ctx.message.reply(
            embeds=[
                error(
                    error=f"Command is on cooldown for `{e.retry_after:.2f}` seconds."
                )
            ]
        )
