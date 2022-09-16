import io
from traceback import format_exception

from discord import File, Interaction
from discord.app_commands import AppCommandError, CommandTree

from .bot import MyBot


class MyTree(CommandTree[MyBot]):
    async def on_error(self, interaction: Interaction, error: AppCommandError) -> None:
        target = await interaction.client.fetch_user(
            interaction.client.owner_id  # type: ignore[attr-defined]
        )
        command = f"`{interaction.command.name}`" if interaction.command else "tree"
        tb = format_exception(type(error), error, error.__traceback__)
        file = File(io.BytesIO("".join(tb).encode()), filename="traceback.txt")
        await target.send(f"Command {command} raised an exception", file=file)

        if interaction.response.is_done():
            await interaction.followup.send(str(error), ephemeral=True)
        else:
            await interaction.response.send_message(str(error))
