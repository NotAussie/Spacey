# Revolt imports
import revolt
from revolt.ext import commands

# View imports
from views import Error


async def errorHandler(ctx: commands.Context, error: Exception):
    if isinstance(error, commands.CommandNotFound):

        await ctx.message.reply(embeds=[Error(f"The entered command does not exist.")])

    elif isinstance(error, commands.errors.CommandOnCooldown):

        await ctx.message.reply(
            embeds=[
                Error(
                    error=f"Command is on cooldown for `{error.retry_after:.2f}` seconds."
                )
            ]
        )
