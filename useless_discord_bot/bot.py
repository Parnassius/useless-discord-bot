from __future__ import annotations

import io
import signal
import tomllib
from pathlib import Path
from sys import exc_info
from traceback import format_exception
from typing import Any

from discord import File, Object
from discord.ext import commands


class MyBot(commands.Bot):
    def __init__(
        self,
        *args: Any,
        test_guild_id: int | None = None,
        config_path: Path,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)

        self.test_guild_id = test_guild_id
        self.config_path = config_path

    def get_config(self, config_file: str) -> dict[Any, Any]:
        file = self.config_path / f"{config_file}.toml"
        try:
            with file.open("rb") as f:
                data = tomllib.load(f)
        except FileNotFoundError:
            data = {}
        return data

    async def setup_hook(self) -> None:
        signal.signal(signal.SIGTERM, signal.getsignal(signal.SIGINT))

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

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        if not self.owner_id:
            return
        target = await self.fetch_user(self.owner_id)
        tb = format_exception(*exc_info())
        file = File(io.BytesIO("".join(tb).encode()), filename="traceback.txt")
        await target.send(f"Handler `{event_method}` raised an exception", file=file)
