from __future__ import annotations

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

    intents = Intents.default()
    intents.members = True

    bot = MyBot(
        commands.when_mentioned,
        tree_cls=MyTree,
        intents=intents,
        owner_id=owner_id,
        help_command=None,
        test_guild_id=test_guild_id,
    )

    bot.run(token)


if __name__ == "__main__":
    main()
