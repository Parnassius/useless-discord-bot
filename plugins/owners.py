import discord  # type: ignore
from discord.ext import commands  # type: ignore

import checks
from bot import MyBot


def setup(bot: MyBot) -> None:
    @bot.command()
    @commands.guild_only()
    @commands.check(checks.is_channel_owner)
    async def addowner(ctx: commands.Context, user: discord.Member) -> None:
        await ctx.channel.set_permissions(
            user, manage_channels=True, manage_messages=True
        )
        await ctx.reply("Done.")

    @bot.command()
    @commands.guild_only()
    async def owners(ctx: commands.Context) -> None:
        owners_list = []
        for k, v in ctx.channel.overwrites.items():
            if isinstance(k, discord.abc.User) and v.manage_channels:
                owners_list.append(k.name)
        if owners_list:
            await ctx.reply(f"Channel owners: {', '.join(owners_list)}.")
        else:
            await ctx.reply("This channel has no owners.")
