from glob import glob
from os.path import basename, dirname, isfile, join

import discord  # type: ignore
from environs import Env

from bot import MyBot

if __name__ == "__main__":
    env = Env()
    env.read_env()

    token = env.str("TOKEN")
    owner_id = env.int("OWNER_ID")

    intents = discord.Intents.default()
    intents.members = True

    bot = MyBot(".", help_command=None, intents=intents, owner_id=owner_id)

    modules = glob(join(dirname(__file__), "plugins", "*.py"))

    for f in modules:
        if isfile(f) and not f.endswith("__init__.py"):
            name = basename(f)[:-3]
            bot.load_extension(f"plugins.{name}")

    bot.run(token)
