from disnake.abc import GuildChannel
from disnake.channel import CategoryChannel, TextChannel
from disnake.interactions.application_command import ApplicationCommandInteraction
from disnake.message import Message

from useless_discord_bot.bot import MyBot


def setup(bot: MyBot) -> None:
    @bot.slash_command(description="Move this channel to another category.")
    async def moveto(
        interaction: ApplicationCommandInteraction, channel: GuildChannel
    ) -> None:
        if interaction.guild is None:
            await interaction.send(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return

        if not isinstance(interaction.channel, TextChannel):
            await interaction.send(
                "This command can only be used in text channels.", ephemeral=True
            )
            return

        if (
            interaction.channel.category is None
            or not interaction.channel.category.overwrites_for(
                interaction.guild.default_role
            ).manage_channels
        ):
            await interaction.send("Cannot move this channel.", ephemeral=True)
            return

        category: CategoryChannel
        after: TextChannel | None
        if isinstance(channel, CategoryChannel):
            category = channel
            after = None
        elif isinstance(channel, TextChannel):
            if channel.category is None:
                await interaction.send(
                    f"Cannot move this channel near the '{channel}' channel.",
                    ephemeral=True,
                )
                return
            category = channel.category
            after = channel
        else:
            await interaction.send(
                "You must specify a category or a text channel.", ephemeral=True
            )
            return

        if not category.overwrites_for(interaction.guild.default_role).manage_channels:
            await interaction.send(
                f"Cannot move this channel to the '{category}' category.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        if after is None:
            await interaction.channel.move(  # type: ignore[call-overload]
                end=True, category=category
            )
        else:
            await interaction.channel.move(  # type: ignore[call-overload]
                after=after, category=category
            )
        await interaction.send("Channel moved.")

    @bot.slash_command(description="Change the name of this channel.")
    async def name(interaction: ApplicationCommandInteraction, new_name: str) -> None:
        if interaction.guild is None:
            await interaction.send(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return

        if (
            interaction.channel.category is None
            or not interaction.channel.category.overwrites_for(
                interaction.guild.default_role
            ).manage_channels
        ):
            await interaction.send("Cannot rename this channel.", ephemeral=True)
            return

        if not new_name or len(new_name) > 100:
            await interaction.send(
                "Channel names should be between 1 and 100 characters long.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        await interaction.channel.edit(name=new_name)
        await interaction.send("Channel name updated.")

    @bot.slash_command(description="Change the topic of this channel.")
    async def topic(interaction: ApplicationCommandInteraction, new_topic: str) -> None:
        if interaction.guild is None:
            await interaction.send(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return

        if not isinstance(interaction.channel, TextChannel):
            await interaction.send(
                "This command can only be used in text channels.", ephemeral=True
            )
            return

        if (
            interaction.channel.category is None
            or not interaction.channel.category.overwrites_for(
                interaction.guild.default_role
            ).manage_channels
        ):
            await interaction.send(
                "Cannot change the topic of this channel.", ephemeral=True
            )
            return

        if not new_topic or len(new_topic) > 1024:
            await interaction.send(
                "Channel topics should be between 1 and 1024 characters long.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        await interaction.channel.edit(topic=new_topic)
        await interaction.send("Channel topic updated.")

    @bot.message_command(name="Pin message")
    async def pin(interaction: ApplicationCommandInteraction, message: Message) -> None:
        if interaction.guild is None:
            await interaction.send(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return

        if (
            interaction.channel.category is None
            or not interaction.channel.category.overwrites_for(
                interaction.guild.default_role
            ).manage_channels
        ):
            await interaction.send(
                "Cannot pin messages in this channel.", ephemeral=True
            )
            return

        if message.pinned:
            await interaction.send("The message is already pinned.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        await message.pin()
        await interaction.send("Message pinned")

    @bot.message_command(name="Unpin message")
    async def unpin(
        interaction: ApplicationCommandInteraction, message: Message
    ) -> None:
        if interaction.guild is None:
            await interaction.send(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return

        if (
            interaction.channel.category is None
            or not interaction.channel.category.overwrites_for(
                interaction.guild.default_role
            ).manage_channels
        ):
            await interaction.send(
                "Cannot unpin messages from this channel.", ephemeral=True
            )

        if not message.pinned:
            await interaction.send("The message is not pinned.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        await message.unpin()
        await interaction.send("Message unpinned")
