from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from peterbot import PeterBot


class Utilities(commands.Cog):
    """
    Various utility commands
    """

    def __init__(self, bot: "PeterBot"):
        self.bot = bot

    @app_commands.command()
    @app_commands.describe(snowflake="user snowflake id or a member")
    async def user(self, interaction: discord.Interaction, snowflake: str):
        """
        Get metadata about a user by their snowflake id
        """
        try:
            user = await self.bot.fetch_user(int(snowflake))
        except (discord.HTTPException, discord.NotFound):
            await interaction.response.send_message(
                f"A user for the id ({snowflake}) was not found"
            )
            return
        user: discord.User
        embed = discord.Embed(title=f"Snowflake: {user.id}", color=2097148)
        embed.add_field(
            name="Discord Id", value=f"{user.name}#{user.discriminator}", inline=False
        )
        embed.add_field(name="Creation Date", value=f"{user.created_at}", inline=False)
        embed.add_field(name="Avatar URL", value=f"{user.display_avatar}")
        embed.set_image(url=user.display_avatar)
        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @app_commands.describe()
    async def guild(self, interaction: discord.Interaction):
        """
        Get metadata about the current guild
        """
        guild = interaction.guild
        embed = discord.Embed(title=guild.name, color=2097148)
        embed.add_field(
            name="Server logging",
            value=str(self.bot.peter_guilds[guild.id]["watch_mode"]),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: "PeterBot") -> None:
    await bot.add_cog(Utilities(bot))
