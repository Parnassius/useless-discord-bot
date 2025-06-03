from __future__ import annotations

import asyncio
import io
import random
import re
import unicodedata
from pathlib import Path
from typing import ClassVar, Self

from discord import File, Interaction, Message, TextChannel, Webhook
from PIL import Image

from useless_discord_bot.bot import MyBot


class GuessTheSpriteGame:
    active_games: ClassVar[dict[TextChannel, Self]] = {}

    def __init__(
        self,
        followup: Webhook,
        channel: TextChannel,
        path: Path,
        species: str,
        form: str,
    ) -> None:
        self.followup = followup
        self.channel = channel
        self.path = path
        self.species = species
        self.form = form

        self.crop_origin: tuple[int, int] | None = None

        self.ended = False

    async def crop_and_send(self, size: int) -> None:
        with Image.open(self.path) as im:
            half_crop = round(min(im.width, im.height) / 10 * size) // 2

            if not self.crop_origin:
                # If the crop origin has not yet been decided (first crop), then get
                # random origin coordinates and crop the image to the required size
                while True:
                    origin_x = random.randint(half_crop, im.width - half_crop)
                    origin_y = random.randint(half_crop, im.height - half_crop)
                    im_cropped = im.crop(
                        (
                            origin_x - half_crop,
                            origin_y - half_crop,
                            origin_x + half_crop,
                            origin_y + half_crop,
                        )
                    )
                    # Try again if there are little to no opaque pixels
                    opaque_pixels = sum(
                        1
                        for alpha in im_cropped.getchannel("A").getdata()
                        if alpha == 255
                    )
                    if opaque_pixels > im_cropped.width * im_cropped.height * 0.25:
                        break

                # Save the coordinates for subsequent crops
                self.crop_origin = origin_x, origin_y

            else:
                # Get the saved coordinates, clamping them to avoid going out of bounds
                origin_x, origin_y = self.crop_origin
                origin_x = max(half_crop, min(origin_x, im.width - half_crop))
                origin_y = max(half_crop, min(origin_y, im.height - half_crop))
                im_cropped = im.crop(
                    (
                        origin_x - half_crop,
                        origin_y - half_crop,
                        origin_x + half_crop,
                        origin_y + half_crop,
                    )
                )

        cropped_image = io.BytesIO()
        im_cropped.save(cropped_image, format="PNG")
        cropped_image.seek(0)
        file = File(cropped_image, filename="image.png")
        await self.followup.send(file=file)

    async def reveal_answer(self, guess_message: Message | None = None) -> None:
        del self.active_games[self.channel]
        self.ended = True

        file = File(self.path)
        if guess_message:
            await guess_message.reply("Correct!", file=file)
        else:
            await self.followup.send(
                f"Time's up, the answer was {self.species}!", file=file
            )


async def setup(bot: MyBot) -> None:
    @bot.listen()
    async def on_message(message: Message) -> None:
        if not isinstance(message.channel, TextChannel):
            return

        game = GuessTheSpriteGame.active_games.get(message.channel)
        if not game:
            return

        guess = "".join(
            [
                c
                for c in unicodedata.normalize("NFKD", message.content)
                if not unicodedata.combining(c)
            ]
        )
        guess = re.sub(r"[^a-z0-9]", "", guess.lower())

        if guess in (game.species, game.form):
            await game.reveal_answer(message)

    @bot.tree.command(description="Guess the Pokémon from a cropped image.")
    async def guessthesprite(interaction: Interaction[MyBot]) -> None:
        if interaction.channel in GuessTheSpriteGame.active_games:
            await interaction.response.send_message(
                "Game already in progress.", ephemeral=True
            )
            return

        if not isinstance(interaction.channel, TextChannel):
            await interaction.response.send_message(
                "This command can only be used in text channels.", ephemeral=True
            )
            return

        await interaction.response.defer()

        path = interaction.client.config_path / "images"
        if random.randrange(128) == 0:
            path /= "shiny"
        else:
            path /= "regular"

        path = random.choice(list(path.iterdir()))
        species = path.stem

        path = random.choice(list(path.iterdir()))
        form = path.stem

        if path.is_dir():
            path = random.choice(list(path.iterdir()))

        game = GuessTheSpriteGame(
            interaction.followup, interaction.channel, path, species, form
        )
        GuessTheSpriteGame.active_games[interaction.channel] = game

        for size in range(4):
            await game.crop_and_send(size + 1)
            await asyncio.sleep(10)
            if game.ended:
                return

        await game.reveal_answer()
