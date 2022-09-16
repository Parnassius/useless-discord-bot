from discord.ext import commands

from useless_discord_bot.bot import MyBot


async def setup(bot: MyBot) -> None:
    @bot.command(hidden=True)
    @commands.is_owner()
    async def kill(ctx: commands.Context) -> None:
        await ctx.bot.close()
