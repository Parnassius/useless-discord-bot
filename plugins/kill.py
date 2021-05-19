from discord.ext import commands  # type: ignore

import checks
from bot import MyBot


def setup(bot: MyBot) -> None:
    @bot.command(hidden=True)
    @commands.check(checks.is_bot_owner)
    async def kill(ctx: commands.Context) -> None:
        await ctx.bot.close()
