import io
from pathlib import Path
from sys import exc_info
from traceback import format_exception
from typing import Any

from discord import File, Object, TextChannel
from discord.abc import GuildChannel
from discord.ext import commands


class MyBot(commands.Bot):
    def __init__(self, *args: Any, test_guild_id: int | None = None, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.test_guild_id = test_guild_id

    async def setup_hook(self) -> None:
        modules = Path(__file__).parent / "plugins"
        for f in modules.glob("*.py"):
            if f.is_file() and f.name != "__init__.py":
                await self.load_extension(f"useless_discord_bot.plugins.{f.stem}")

        if self.test_guild_id:
            test_guild = Object(id=self.test_guild_id)
            self.tree.copy_global_to(guild=test_guild)
            await self.tree.sync(guild=test_guild)
        else:
            await self.tree.sync()

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
        file = File(io.BytesIO("".join(tb).encode()), filename="traceback.txt")
        await target.send(f"Handler `{event_method}` raised an exception", file=file)

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
