from sys import exc_info
from traceback import format_tb
from typing import Any

import discord  # type: ignore
from discord.ext import commands  # type: ignore


class MyBot(commands.Bot):
    async def on_ready(self) -> None:
        print(f"Logged on as {self.user}!")

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        target: discord.abc.Messageable = await self.fetch_user(self.owner_id)
        for i in args:
            if isinstance(i, discord.abc.Messageable):
                target = i
                break
        _, val, tb = exc_info()
        await target.send(
            f"Handler `{event_method}` raised an exception: {val}\n"
            f"```{''.join(format_tb(tb))}```"
        )

    async def on_command_error(
        self, context: commands.Context, exception: commands.CommandError
    ) -> None:
        if isinstance(exception, commands.errors.CommandNotFound):
            return
        msg = str(exception)
        if (
            isinstance(exception, discord.ext.commands.errors.CommandInvokeError)
            and not isinstance(exception.original, discord.HTTPException)
            and exception.__traceback__
        ):
            msg += f"\n```{''.join(format_tb(exception.__traceback__))}```"
        await context.reply(msg)

    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        if not isinstance(channel, discord.TextChannel):
            return

        await channel.set_permissions(channel.guild.default_role, manage_channels=None)

        creator = (
            await channel.guild.audit_logs(
                action=discord.AuditLogAction.channel_create
            ).get(target=channel)
        ).user
        await channel.set_permissions(
            creator, manage_channels=True, manage_messages=True
        )
