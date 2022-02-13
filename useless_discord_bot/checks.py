from disnake.ext import commands


def is_bot_owner(ctx: commands.Context) -> bool:
    if ctx.author.id != ctx.bot.owner_id:
        raise commands.CommandError("You do not own this bot.")
    return True
