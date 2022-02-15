# pylint: disable=no-self-use

from sys import exc_info
from traceback import format_exception
from typing import Any

from disnake.abc import GuildChannel
from disnake.channel import TextChannel
from disnake.ext import commands
from disnake.interactions.application_command import ApplicationCommandInteraction


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
        target = await self.fetch_user(self.owner_id)
        tb = format_exception(*exc_info())
        await target.send(
            f"Handler `{event_method}` raised an exception:\n" f"```{''.join(tb)}```"
        )

    async def on_message_command_error(
        self,
        interaction: ApplicationCommandInteraction,
        exception: commands.CommandError,
    ) -> None:
        target = await self.fetch_user(self.owner_id)
        command = interaction.application_command.name
        tb = format_exception(type(exception), exception, exception.__traceback__)
        await target.send(
            f"Message command `{command}` raised an exception:\n" f"```{''.join(tb)}```"
        )

        await interaction.send(str(exception), ephemeral=True)

    async def on_slash_command_error(
        self,
        interaction: ApplicationCommandInteraction,
        exception: commands.CommandError,
    ) -> None:
        target = await self.fetch_user(self.owner_id)
        command = interaction.application_command.name
        tb = format_exception(type(exception), exception, exception.__traceback__)
        await target.send(
            f"Slash command `{command}` raised an exception:\n" f"```{''.join(tb)}```"
        )

        await interaction.send(str(exception), ephemeral=True)

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
