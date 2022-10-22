from discord import CategoryChannel, Interaction, Message, TextChannel
from discord.abc import GuildChannel

from useless_discord_bot.bot import MyBot


async def setup(bot: MyBot) -> None:
    @bot.listen()
    async def on_ready() -> None:
        for guild in bot.guilds:
            if not guild.me.guild_permissions.manage_roles:
                continue
            for category in guild.categories:
                if not category.overwrites_for(guild.default_role).manage_channels:
                    continue
                for channel in category.text_channels:
                    if not channel.overwrites_for(guild.default_role).manage_channels:
                        continue
                    await channel.set_permissions(
                        channel.guild.default_role, manage_channels=None
                    )

    @bot.listen()
    async def on_guild_channel_create(channel: GuildChannel) -> None:
        if not isinstance(channel, TextChannel):
            return

        if (
            channel.guild.me.guild_permissions.manage_roles
            and channel.category
            and channel.category.overwrites_for(
                channel.guild.default_role
            ).manage_channels
        ):
            await channel.set_permissions(
                channel.guild.default_role, manage_channels=None
            )

    @bot.tree.command(description="Move this channel to another category.")
    async def moveto(interaction: Interaction, channel: GuildChannel) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return

        if not isinstance(interaction.channel, TextChannel):
            await interaction.response.send_message(
                "This command can only be used in text channels.", ephemeral=True
            )
            return

        if (
            interaction.channel.category is None
            or not interaction.channel.category.overwrites_for(
                interaction.guild.default_role
            ).manage_channels
        ):
            await interaction.response.send_message(
                "Cannot move this channel.", ephemeral=True
            )
            return

        category: CategoryChannel
        after: TextChannel | None
        if isinstance(channel, CategoryChannel):
            category = channel
            after = None
        elif isinstance(channel, TextChannel):
            if channel.category is None:
                await interaction.response.send_message(
                    f"Cannot move this channel near the '{channel}' channel.",
                    ephemeral=True,
                )
                return
            category = channel.category
            after = channel
        else:
            await interaction.response.send_message(
                "You must specify a category or a text channel.", ephemeral=True
            )
            return

        if not category.overwrites_for(interaction.guild.default_role).manage_channels:
            await interaction.response.send_message(
                f"Cannot move this channel to the '{category}' category.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        if after is None:
            await interaction.channel.move(end=True, category=category)
        else:
            await interaction.channel.move(after=after, category=category)
        await interaction.followup.send("Channel moved.")

    @bot.tree.command(description="Change the name of this channel.")
    async def name(interaction: Interaction, new_name: str) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return

        assert isinstance(interaction.channel, GuildChannel)

        if (
            interaction.channel.category is None
            or not interaction.channel.category.overwrites_for(
                interaction.guild.default_role
            ).manage_channels
        ):
            await interaction.response.send_message(
                "Cannot rename this channel.", ephemeral=True
            )
            return

        if not new_name or len(new_name) > 100:
            await interaction.response.send_message(
                "Channel names should be between 1 and 100 characters long.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        await interaction.channel.edit(name=new_name)
        await interaction.followup.send("Channel name updated.")

    @bot.tree.command(description="Change the topic of this channel.")
    async def topic(interaction: Interaction, new_topic: str) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return

        if not isinstance(interaction.channel, TextChannel):
            await interaction.response.send_message(
                "This command can only be used in text channels.", ephemeral=True
            )
            return

        if (
            interaction.channel.category is None
            or not interaction.channel.category.overwrites_for(
                interaction.guild.default_role
            ).manage_channels
        ):
            await interaction.response.send_message(
                "Cannot change the topic of this channel.", ephemeral=True
            )
            return

        if not new_topic or len(new_topic) > 1024:
            await interaction.response.send_message(
                "Channel topics should be between 1 and 1024 characters long.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        await interaction.channel.edit(topic=new_topic)
        await interaction.followup.send("Channel topic updated.")

    @bot.tree.context_menu(name="Pin message")
    async def pin(interaction: Interaction, message: Message) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return

        assert isinstance(interaction.channel, GuildChannel)

        if (
            interaction.channel.category is None
            or not interaction.channel.category.overwrites_for(
                interaction.guild.default_role
            ).manage_channels
        ):
            await interaction.response.send_message(
                "Cannot pin messages in this channel.", ephemeral=True
            )
            return

        if message.pinned:
            await interaction.response.send_message(
                "The message is already pinned.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        await message.pin()
        await interaction.followup.send("Message pinned")

    @bot.tree.context_menu(name="Unpin message")
    async def unpin(interaction: Interaction, message: Message) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command cannot be used in DMs.", ephemeral=True
            )
            return

        assert isinstance(interaction.channel, GuildChannel)

        if (
            interaction.channel.category is None
            or not interaction.channel.category.overwrites_for(
                interaction.guild.default_role
            ).manage_channels
        ):
            await interaction.response.send_message(
                "Cannot unpin messages from this channel.", ephemeral=True
            )
            return

        if not message.pinned:
            await interaction.response.send_message(
                "The message is not pinned.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        await message.unpin()
        await interaction.followup.send("Message unpinned")
