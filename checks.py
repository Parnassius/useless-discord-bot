from discord.ext import commands  # type: ignore


def is_bot_owner(ctx: commands.Context) -> bool:
    if ctx.author.id != ctx.bot.owner_id:
        raise commands.CommandError("You do not own this bot.")
    return True


def is_channel_owner(ctx: commands.Context) -> bool:
    if not ctx.channel.permissions_for(ctx.author).manage_channels:
        raise commands.CommandError("You do not own this channel.")
    return True
