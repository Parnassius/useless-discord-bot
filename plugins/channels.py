from typing import TypedDict, Union

import discord  # type: ignore
from discord.ext import commands  # type: ignore

from bot import MyBot


def setup(bot: MyBot) -> None:
    @bot.command()
    @commands.guild_only()
    async def moveto(
        ctx: commands.Context,
        channel: Union[discord.CategoryChannel, discord.TextChannel],
    ) -> None:
        if not ctx.channel.category.overwrites_for(
            ctx.guild.default_role
        ).manage_channels:
            await ctx.reply("Cannot move this channel.")
            return

        class KwargsDict(TypedDict, total=False):
            end: bool
            after: discord.TextChannel
            category: discord.CategoryChannel

        kwargs: KwargsDict
        if isinstance(channel, discord.CategoryChannel):
            kwargs = {"end": True, "category": channel}
        else:
            kwargs = {"after": channel, "category": channel.category}

        if (
            not kwargs["category"]
            .overwrites_for(ctx.guild.default_role)
            .manage_channels
        ):
            await ctx.reply(
                f"Cannot move this channel to the '{kwargs['category']}' category."
            )
            return

        await ctx.channel.move(**kwargs)
        await ctx.message.delete()
