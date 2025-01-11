from __future__ import annotations

from discord import Member, VoiceState

from useless_discord_bot.bot import MyBot


async def setup(bot: MyBot) -> None:
    @bot.listen()
    async def on_voice_state_update(
        member: Member, before: VoiceState, after: VoiceState
    ) -> None:
        if not member.guild.me.guild_permissions.manage_roles:
            return

        if before.channel == after.channel:
            return

        if before.channel is not None:
            role = next(
                (x for x in member.guild.roles if x.name == f"call-{before.channel}"),
                None,
            )
            if role:
                await member.remove_roles(role)

        if after.channel is not None:
            role = next(
                (x for x in member.guild.roles if x.name == f"call-{after.channel}"),
                None,
            )
            if role:
                await member.add_roles(role)
