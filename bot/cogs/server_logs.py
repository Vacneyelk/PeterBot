from discord.ext import commands
from discord import app_commands
import discord

from database import updaters, readers

import tempfile

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from peterbot import PeterBot


class ServerLogs(commands.Cog):
    def __init__(self, bot: "PeterBot"):
        self.bot = bot

    @app_commands.command()
    @app_commands.describe(
        mode="True: enables server logging\nFalse: disables server logging"
    )
    @commands.has_permissions(administrator=True)
    async def server_watch(self, interaction: discord.Interaction, mode: bool):
        """
        updates the server watch mode
        """
        current_guild = interaction.guild.id
        await updaters.update_guild_watch(self.bot, current_guild, mode)
        current_watch_mode: str
        if mode is True:
            current_watch_mode = "enabled"
        else:
            current_watch_mode = "disabled"
        await interaction.response.send_message(
            f"Server logging is now {current_watch_mode}"
        )

    @app_commands.command()
    @app_commands.describe(snowflake="user snowflake id")
    @commands.has_permissions(administrator=True)
    async def user_logs(self, interaction: discord.Interaction, snowflake: int):
        """
        Retrieves user logs as a file
        """
        try:
            await self.bot.fetch_user(snowflake)
        except (discord.HTTPException, discord.NotFound):
            await interaction.response.send_message(f'User with snowflake {snowflake} does not exist')
            return
        guild_id = interaction.guild.id
        logs = await readers.get_user_logs(self.bot, guild_id, snowflake)
        with tempfile.TemporaryDirectory() as tmp_dir:
            with open(f"{tmp_dir}/user_logs.txt", "w") as f:
                for log in logs:
                    f.write(
                        f"{log['message_type']} - {log['message_id']} - "
                        f"{log['message_date']}\n{log['message']}\n\n"
                    )

            with open(f"{tmp_dir}/user_logs.txt", "rb") as f_rb:
                await interaction.response.send_message(
                    file=discord.File(f_rb, filename=f"user_log_{snowflake}.txt")
                )

    @app_commands.command()
    @app_commands.describe(snowflake="channel snowflake id")
    @commands.has_permissions(administrator=True)
    async def channel_logs(self, interaction: discord.Interaction, snowflake: int):
        """
        Retrieves channel logs as a file
        """
        guild_id = interaction.guild.id
        try:
            await self.bot.fetch_channel(snowflake)
        except (discord.HTTPException, discord.NotFound):
            await interaction.response.send_message(f'Channel with snowflake {snowflake} does not exist')
            return
        logs = await readers.get_channel_logs(self.bot, guild_id, snowflake)
        with tempfile.TemporaryDirectory() as tmp_dir:
            with open(f"{tmp_dir}/channel_logs.txt", "w") as f:
                for log in logs:
                    f.write(
                        f"{log['message_type']} - {log['message_id']} - {log['message_date']}\n{log['message']}\n\n"
                    )

            with open(f"{tmp_dir}/channel_logs.txt", "rb") as f_rb:
                await interaction.response.send_message(
                    file=discord.File(f_rb, filename=f"channel_log_{snowflake}.txt")
                )


async def setup(bot: "PeterBot") -> None:
    await bot.add_cog(ServerLogs(bot))
