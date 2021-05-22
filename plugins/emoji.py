import xml.etree.ElementTree as ET

import aiohttp
from cairosvg import svg2png  # type: ignore
from discord.ext import commands  # type: ignore

from bot import MyBot

TWEMOJI_URL = (
    "https://raw.githubusercontent.com/twitter/twemoji/master/assets/svg/{}.svg"
)


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

        emoji_url = TWEMOJI_URL.format(to_code_point(emoji))
        async with aiohttp.ClientSession() as session:
            async with session.get(emoji_url) as resp:
                if resp.status != 200:
                    await ctx.reply("Emoji not found.")
                    return
                svg = ET.fromstring(await resp.text())

        tags = svg.findall(".//*[@fill]")
        if len(tags) != len(colors):
            await ctx.reply(
                f"This emoji needs {len(tags)} colors, {len(colors)} were provided."
            )
            return
        for tag, color in zip(tags, colors):
            tag.set("fill", color)

        img = svg2png(bytestring=ET.tostring(svg, encoding="unicode"), output_width=128)

        new_emoji = await ctx.guild.create_custom_emoji(name=emoji_name, image=img)
        await ctx.message.add_reaction(new_emoji)
