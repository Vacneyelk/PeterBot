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
        user = self.bot.get_user(int(snowflake))
        if user is None:
            await interaction.response.send_message(
                f"A user for the id ({user}) was not found"
            )
        user: discord.User
        embed = discord.Embed(title=f"Snowflake: {user.id}", color=2097148)
        embed.add_field(
            name="Discord Id", value=f"{user.name}#{user.discriminator}", inline=False
        )
        embed.add_field(name="Creation Date", value=f"{user.created_at}", inline=False)
        embed.add_field(name="Avatar URL", value=f"{user.display_avatar}")
        embed.set_image(url=user.display_avatar)
        await interaction.response.send_message(embed=embed)


async def setup(bot: "PeterBot") -> None:
    await bot.add_cog(Utilities(bot))
