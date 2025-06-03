from __future__ import annotations

from pathlib import Path

from discord import Intents
from discord.ext import commands
from typenv import Env

from useless_discord_bot.bot import MyBot
from useless_discord_bot.tree import MyTree


def main() -> None:
    env = Env()
    env.read_env()

    token = env.str("TOKEN")
    owner_id = env.int("OWNER_ID")
    test_guild_id = env.int("TEST_GUILD_ID", default=None)
    config_path = Path(__file__).parent.parent.parent / "config"
    if config_path_ := env.str("BOT_CONFIG_PATH", default=""):
        config_path = Path(config_path_)

    intents = Intents.default()
    intents.message_content = True

    bot = MyBot(
        commands.when_mentioned,
        tree_cls=MyTree,
        intents=intents,
        owner_id=owner_id,
        help_command=None,
        test_guild_id=test_guild_id,
        config_path=config_path,
    )

    bot.run(token)


if __name__ == "__main__":
    main()
