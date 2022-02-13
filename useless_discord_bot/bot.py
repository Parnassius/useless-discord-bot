# pylint: disable=no-self-use

from sys import exc_info
from traceback import format_tb
from typing import Any

from disnake.abc import GuildChannel, Messageable
from disnake.channel import TextChannel
from disnake.errors import HTTPException
from disnake.ext import commands


class MyBot(commands.Bot):
    async def on_ready(self) -> None:
        print(f"Logged on as {self.user}!")

        for guild in self.guilds:
            if not guild.me.guild_permissions.manage_roles:
                continue
            for category in guild.categories:
                if not category.overwrites_for(guild.default_role).manage_channels:
                    continue
                for channel in category.text_channels:
                    if not channel.overwrites_for(guild.default_role).manage_channels:
                        continue
                    await channel.set_permissions(
                        channel.guild.default_role, manage_channels=None
                    )

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        # pylint: disable=unused-argument
        target: Messageable = await self.fetch_user(self.owner_id)
        for i in args:
            if isinstance(i, Messageable):
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
            isinstance(exception, commands.errors.CommandInvokeError)
            and not isinstance(exception.original, HTTPException)
            and exception.__traceback__
        ):
            msg += f"\n```{''.join(format_tb(exception.__traceback__))}```"
        await context.reply(msg)

    async def on_guild_channel_create(self, channel: GuildChannel) -> None:
        if not isinstance(channel, TextChannel):
            return

        if (
            channel.guild.me.guild_permissions.manage_roles
            and channel.category
            and channel.category.overwrites_for(
                channel.guild.default_role
            ).manage_channels
        ):
            await channel.set_permissions(
                channel.guild.default_role, manage_channels=None
            )
