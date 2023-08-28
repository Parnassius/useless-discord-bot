from __future__ import annotations

from cairosvg import svg2png  # type: ignore[import]
from discord import (
    Embed,
    Emoji,
    Guild,
    Interaction,
    Member,
    Object,
    Role,
    SelectOption,
    TextChannel,
)
from discord.ui import Button, Select, View

from useless_discord_bot.bot import MyBot


class SelfRoleSelect(Select[View]):
    def __init__(
        self,
        *,
        placeholder: str,
        unique: bool,
        roles: dict[Role, tuple[Emoji | None, int]],
        member: Member,
    ) -> None:
        self.roles = roles
        super().__init__(
            custom_id="roles",
            placeholder=placeholder,
            min_values=0,
            max_values=1 if unique else len(self.roles),
            options=[
                SelectOption(
                    label=role.name,
                    value=str(role.id),
                    emoji=emoji,
                    default=role in member.roles,
                )
                for role, (emoji, _) in self.roles.items()
            ],
        )

    async def callback(
        self, interaction: Interaction[MyBot]  # type: ignore[override]
    ) -> None:
        member = interaction.user
        assert isinstance(member, Member)

        await interaction.response.defer(ephemeral=True, thinking=True)

        added_role_ids = {int(x) for x in self.values}
        removed_roles = (x for x in self.roles.keys() if x.id not in added_role_ids)
        added_roles = (Object(x) for x in added_role_ids)

        await member.remove_roles(*removed_roles)
        await member.add_roles(*added_roles)

        await interaction.followup.send("Roles updated.")


class SelfRoleButton(Button["SelfRoleButtonsView"]):
    def __init__(
        self, *, label: str, unique: bool, roles: dict[Role, tuple[Emoji | None, int]]
    ) -> None:
        self.label: str
        super().__init__(label=label)
        self.unique = unique
        self.roles = roles

    async def callback(
        self, interaction: Interaction[MyBot]  # type: ignore[override]
    ) -> None:
        member = interaction.user
        assert isinstance(member, Member)

        view = View()
        select = SelfRoleSelect(
            placeholder=self.label, unique=self.unique, roles=self.roles, member=member
        )
        view.add_item(select)
        await interaction.response.send_message(view=view, ephemeral=True)


class SelfRoleButtonsView(View):
    def __init__(
        self,
        *,
        data: list[tuple[str, bool, dict[Role, tuple[Emoji | None, int]]]],
    ) -> None:
        super().__init__(timeout=None)
        for label, unique, roles in data:
            self.add_item(SelfRoleButton(label=label, unique=unique, roles=roles))


async def setup(bot: MyBot) -> None:
    @bot.listen()
    async def on_ready() -> None:
        self_roles = bot.get_config("self_roles")
        self_role_emoji = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36">'
            '<circle fill="#{}" cx="18" cy="18" r="18"/>'
            "</svg>"
        )

        old_emojis = {}
        used_emojis = []

        dummy_emoji_guild = self_roles.get("dummy_emoji_guild", 0)
        assert isinstance(dummy_emoji_guild, int)

        for message_data in self_roles.get("messages", []):
            channel = bot.get_channel(int(message_data["channel"]))
            assert isinstance(channel, TextChannel)
            message = await channel.fetch_message(int(message_data["message"]))
            emoji_guild = bot.get_guild(dummy_emoji_guild or channel.guild.id)
            assert isinstance(emoji_guild, Guild)
            embeds = []
            view_data = []
            for section in message_data["sections"]:
                old_emojis.update(
                    {
                        (emoji_guild.id, x.name): x
                        for x in emoji_guild.emojis
                        if x.name.startswith("selfrole_")
                    }
                )
                unique = bool(section.get("unique"))
                message_content = section.get("msg")
                button_content = section.get("btn")
                roles = {}
                for role_id in section["roles"]:
                    if isinstance(role_id, list):
                        role_id, role_channel_id = role_id
                    else:
                        role_channel_id = None

                    role = channel.guild.get_role(role_id)

                    if role is None:
                        continue
                    if role.color.value == 0:
                        emoji = None
                    else:
                        name = f"selfrole_{role.color.value}"
                        if (emoji_guild.id, name) in old_emojis:
                            emoji = old_emojis[emoji_guild.id, name]
                        else:
                            role_color = "".join(
                                f"{x:02X}" for x in role.color.to_rgb()
                            )
                            image = svg2png(
                                bytestring=self_role_emoji.format(role_color),
                                output_width=128,
                            )
                            emoji = await emoji_guild.create_custom_emoji(
                                name=name, image=image
                            )
                        used_emojis.append(emoji)
                    roles[role] = emoji, role_channel_id

                descriptions = []
                for role, (_, role_channel_id) in roles.items():
                    description = f"<@&{role.id}>"
                    if role_channel_id:
                        description += f" <#{role_channel_id}>"
                    descriptions.append(description)
                embeds.append(
                    Embed(title=message_content, description="\n".join(descriptions))
                )
                view_data.append((button_content, unique, roles))

            view = SelfRoleButtonsView(data=view_data)

            await message.edit(content="", embeds=embeds, view=view)

        for emoji in old_emojis.values():
            if emoji not in used_emojis:
                await emoji.delete()
