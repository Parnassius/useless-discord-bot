import io
import xml.etree.ElementTree as ET
from collections.abc import Awaitable, Callable

import aiohttp
from cairosvg import svg2png  # type: ignore
from disnake.embeds import Embed
from disnake.file import File
from disnake.interactions.application_command import ApplicationCommandInteraction
from disnake.interactions.base import Interaction
from disnake.interactions.message import MessageInteraction
from disnake.interactions.modal import ModalInteraction
from disnake.ui.button import Button
from disnake.ui.modal import Modal
from disnake.ui.text_input import TextInput
from disnake.ui.view import View
from PIL import Image, ImageColor, ImageDraw  # type: ignore

from useless_discord_bot.bot import MyBot

ET.register_namespace("", "http://www.w3.org/2000/svg")

TWEMOJI_URL = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/"
TWEMOJI_SVG_URL = f"{TWEMOJI_URL}svg/{{}}.svg"
TWEMOJI_PNG_URL = f"{TWEMOJI_URL}72x72/{{}}.png"


class ChangeColorModal(Modal):
    def __init__(self, *, num: int, color: str, view: "ChangeColorView") -> None:
        super().__init__(
            title=f"Edit color {num+1}",
            components=TextInput(label="Color", custom_id="color", placeholder=color),
        )
        self.num = num
        self.view = view

    async def callback(self, interaction: ModalInteraction, /) -> None:
        self.view.colors[self.num] = interaction.text_values["color"]
        await self.view.update_embed(interaction)


class ChangeColorButton(Button["ChangeColorView"]):
    def __init__(self, *, num: int, color: str) -> None:
        self.view: ChangeColorView
        super().__init__(label=f"Edit color {num+1}", custom_id=f"color{num}")
        self.num = num
        self.color = color

    async def callback(self, interaction: MessageInteraction) -> None:
        modal = ChangeColorModal(
            num=self.num,
            color=self.color,
            view=self.view,
        )
        await interaction.response.send_modal(modal)


class ChangeColorView(View):
    def __init__(
        self,
        *,
        colors: list[str],
        update_embed: Callable[[ModalInteraction], Awaitable[None]],
    ) -> None:
        super().__init__()
        self.colors = colors
        self.update_embed = update_embed

        for num, color in enumerate(colors):
            self.add_item(ChangeColorButton(num=num, color=color))


class ColorEmoji:
    def __init__(
        self,
        interaction: ApplicationCommandInteraction,
        new_emoji_name: str,
        svg: str,
    ) -> None:
        self.interaction = interaction

        self.new_emoji_name = new_emoji_name
        self.svg = svg

        tags = ET.fromstring(self.svg).findall(".//*[@fill]")
        self.original_colors = sorted(x for x in (i.get("fill") for i in tags) if x)
        self.colors = self.original_colors.copy()

    async def send_embed(self, thumbnail_url: str) -> None:
        await self._send_embed(thumbnail_url=thumbnail_url)

    async def update_embed(self, interaction: ModalInteraction) -> None:
        await self._send_embed(interaction=interaction)

    async def _send_embed(
        self,
        *,
        thumbnail_url: str | None = None,
        interaction: Interaction | None = None,
    ) -> None:
        files = []
        embed = Embed()

        if thumbnail_url is not None:
            embed.set_thumbnail(url=thumbnail_url)
        else:
            embed.set_thumbnail(url="attachment://emoji.png")
            files.append(File(self._emoji_image(), filename="emoji.png"))

        embed.set_image(url="attachment://colors.png")
        files.append(File(self._colors_image(), filename="colors.png"))

        for n, c in enumerate(self.colors, 1):
            embed.add_field(name=f"Color {n}", value=c)

        view = ChangeColorView(colors=self.colors, update_embed=self.update_embed)

        if interaction is None:
            interaction = self.interaction

        await interaction.send(embed=embed, files=files, view=view, ephemeral=True)

    def _colors_image(self) -> io.BytesIO:
        with Image.new("RGB", (420, 100)) as im:
            draw = ImageDraw.Draw(im)
            section_width = im.width / len(self.colors)
            for n, c in enumerate(self.colors):
                start = int(section_width * n)
                end = int(section_width * (n + 1))
                draw.rectangle(
                    [(start, 0), (end, im.height)],
                    ImageColor.getrgb(c),
                )
            colors_image = io.BytesIO()
            im.save(colors_image, format="PNG")
        colors_image.seek(0)
        return colors_image

    def _emoji_image(self) -> io.BytesIO:
        svg_image = ET.fromstring(self.svg)
        tags = svg_image.findall(".//*[@fill]")
        color_mappings = dict(zip(self.original_colors, self.colors))
        for tag in tags:
            color = tag.get("fill")
            if color is not None:
                tag.set("fill", color_mappings[color])
        image = svg2png(
            bytestring=ET.tostring(svg_image, encoding="unicode"), output_width=128
        )
        return io.BytesIO(image)


def to_code_point(unicode_surrogates: str) -> str:
    r = []
    c = 0
    p = 0
    for i in unicode_surrogates:
        c = ord(i)
        if p:
            r.append(format(0x10000 + ((p - 0xD800) << 10) + (c - 0xDC00), "x"))
            p = 0
        elif 0xD800 <= c <= 0xDBFF:
            p = c
        else:
            r.append(format(c, "x"))
    if len(r) == 2 and r[1] == "fe0f":
        del r[1]
    return "-".join(r)


def setup(bot: MyBot) -> None:
    @bot.slash_command(
        description="Create a new emoji by changing the colors of a default one."
    )
    async def coloremoji(
        interaction: ApplicationCommandInteraction, emoji: str, new_emoji_name: str
    ) -> None:
        emoji_code_point = to_code_point(emoji)
        emoji_svg_url = TWEMOJI_SVG_URL.format(emoji_code_point)
        emoji_png_url = TWEMOJI_PNG_URL.format(emoji_code_point)
        async with aiohttp.ClientSession() as session:
            async with session.get(emoji_svg_url) as resp:
                if resp.status != 200:
                    await interaction.send("Emoji not found.", ephemeral=True)
                    return
                svg = await resp.text()

        ce = ColorEmoji(interaction, new_emoji_name, svg)

        await ce.send_embed(emoji_png_url)
