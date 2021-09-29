import io
import xml.etree.ElementTree as ET

import aiohttp
import discord  # type: ignore
from cairosvg import svg2png  # type: ignore
from discord.ext import commands  # type: ignore
from PIL import Image, ImageColor, ImageDraw  # type: ignore

from useless_discord_bot.bot import MyBot

TWEMOJI_URL = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/"
TWEMOJI_SVG_URL = f"{TWEMOJI_URL}svg/{{}}.svg"
TWEMOJI_PNG_URL = f"{TWEMOJI_URL}72x72/{{}}.png"


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
    @bot.command()
    @commands.guild_only()
    async def coloremoji(
        ctx: commands.Context, emoji: str, emoji_name: str, *colors: str
    ) -> None:
        ET.register_namespace("", "http://www.w3.org/2000/svg")

        emoji_code_point = to_code_point(emoji)
        emoji_svg_url = TWEMOJI_SVG_URL.format(emoji_code_point)
        emoji_png_url = TWEMOJI_PNG_URL.format(emoji_code_point)
        async with aiohttp.ClientSession() as session:
            async with session.get(emoji_svg_url) as resp:
                if resp.status != 200:
                    await ctx.reply("Emoji not found.")
                    return
                svg = ET.fromstring(await resp.text())

        tags = svg.findall(".//*[@fill]")
        original_colors = sorted(
            {i.get("fill") for i in tags}  # type: ignore[type-var]
        )

        if len(original_colors) != len(colors):
            try:
                ImageColor.getrgb(emoji_name)
            except ValueError:
                pass
            else:
                colors = (emoji_name, *colors)
                emoji_name = "new_emoji"

        if len(original_colors) != len(colors):
            with Image.new("RGB", (420, 100)) as im:
                draw = ImageDraw.Draw(im)
                section_width = im.width / len(original_colors)
                for n, c in enumerate(original_colors):
                    start = int(section_width * n)
                    end = int(section_width * (n + 1))
                    draw.rectangle(
                        [(start, 0), (end, im.height)],
                        ImageColor.getrgb(c),
                    )
                colors_image = io.BytesIO()
                im.save(colors_image, format="PNG")
            colors_image.seek(0)

            embed = discord.Embed(title="Original colors")

            embed.set_thumbnail(url=emoji_png_url)
            embed.set_image(url="attachment://colors.png")
            for n, c in enumerate(original_colors, 1):
                embed.add_field(name=f"Color {n}", value=c)
            await ctx.reply(
                (
                    f"This emoji needs {len(original_colors)} colors, "
                    f"{len(colors)} were provided."
                ),
                file=discord.File(colors_image, filename="colors.png"),
                embed=embed,
            )
            return

        color_mappings = dict(zip(original_colors, colors))
        for tag in tags:
            tag.set("fill", color_mappings[tag.get("fill")])

        img = svg2png(bytestring=ET.tostring(svg, encoding="unicode"), output_width=128)

        new_emoji = await ctx.guild.create_custom_emoji(name=emoji_name, image=img)
        await ctx.message.add_reaction(new_emoji)
