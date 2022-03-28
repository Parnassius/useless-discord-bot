from glob import glob
from os.path import basename, dirname, isfile, join

from disnake.flags import Intents
from typenv import Env

from .bot import MyBot


def main() -> None:
    env = Env()
    env.read_env()

    token = env.str("TOKEN")
    owner_id = env.int("OWNER_ID")

    intents = Intents.default()
    intents.members = True  # pylint: disable=assigning-non-slot

    bot = MyBot(
        ".",
        intents=intents,
        owner_id=owner_id,
        help_command=None,
    )

    modules = glob(join(dirname(__file__), "plugins", "*.py"))

    for f in modules:
        if isfile(f) and not f.endswith("__init__.py"):
            name = basename(f)[:-3]
            bot.load_extension(f"useless_discord_bot.plugins.{name}")

    bot.run(token)


if __name__ == "__main__":
    main()
