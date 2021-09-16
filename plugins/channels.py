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

    @bot.command()
    @commands.guild_only()
    async def name(ctx: commands.Context, *name_parts: str) -> None:
        if not ctx.channel.category.overwrites_for(
            ctx.guild.default_role
        ).manage_channels:
            await ctx.reply("Cannot rename this channel.")
            return

        new_name = " ".join(name_parts)

        if not new_name or len(new_name) > 100:
            await ctx.reply(
                "Channel names should be between 1 and 100 characters long."
            )
            return

        await ctx.channel.edit(name=new_name)
        await ctx.reply("Done.")

    @bot.command()
    @commands.guild_only()
    async def topic(ctx: commands.Context, *topic_parts: str) -> None:
        if not ctx.channel.category.overwrites_for(
            ctx.guild.default_role
        ).manage_channels:
            await ctx.reply("Cannot change the topic of this channel.")
            return

        new_topic = " ".join(topic_parts)

        if not new_topic or len(new_topic) > 1024:
            await ctx.reply(
                "Channel topics should be between 1 and 1024 characters long."
            )
            return

        await ctx.channel.edit(topic=new_topic)
        await ctx.reply("Done.")

    @bot.command(aliases=["unpin"])
    @commands.guild_only()
    async def pin(ctx: commands.Context) -> None:
        unpin = ctx.invoked_with == "unpin"

        if not ctx.channel.category.overwrites_for(
            ctx.guild.default_role
        ).manage_channels:
            if unpin:
                await ctx.reply("Cannot unpin messages from this channel.")
            else:
                await ctx.reply("Cannot pin messages in this channel.")
            return

        if ctx.message.reference is None:
            if unpin:
                await ctx.reply("Please reply to the message I should unpin.")
            else:
                await ctx.reply("Please reply to the message I should pin.")
            return

        msg = ctx.message.reference.resolved

        if not isinstance(msg, discord.Message):
            await ctx.reply("Unable to fetch the message.")
            return

        if unpin:
            if not msg.pinned:
                await ctx.reply("The message is not pinned.")
                return
            await msg.unpin()
            await ctx.reply("Done.")
        else:
            if msg.pinned:
                await ctx.reply("The message is already pinned.")
                return
            await msg.pin()
