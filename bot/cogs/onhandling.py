from typing import TYPE_CHECKING

import discord
from database import writers
from discord.ext import commands

if TYPE_CHECKING:
    from peterbot import PeterBot


class OnHandling(commands.Cog):
    def __init__(self, bot: "PeterBot"):
        self.bot = bot
        self.valid_message_types = [
            "Original",
            "Edit: before",
            "Edit: after",
            "Deletion",
        ]

    async def log_message(self, message: discord.Message, message_type: str) -> None:
        """
        logs a message to the database

        Parameters
        ----------
        message : discord.Message
            message and all associated content
        message_type : str
            the type of message being logged
            messages can be Original, Edit: before, Edit: after, Deletion

        Returns
        -------
        None
        """
        await writers.insert_user_message(
            self.bot,
            message.guild.id,
            message.channel.id,
            message.author.id,
            message.id,
            message.clean_content,
            message_type,
            message.created_at,
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        on_message listener for additional on_message handling
        """
        if message.author.bot:
            return
        msg_guild = message.guild.id

        if self.bot.peter_guilds[msg_guild]["watch_mode"]:
            await self.log_message(message, "Original")

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """
        on_message_edit listener for additional edit handling
        """
        if before.author.bot:
            return
        msg_guild = before.guild.id

        if self.bot.peter_guilds[msg_guild]["watch_mode"]:
            await self.log_message(before, "Edit: before")
            await self.log_message(after, "Edit: after")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """
        on_message_delete listener for additional edit handling
        """
        if message.author.bot:
            return
        msg_guild = message.guild.id

        if self.bot.peter_guilds[msg_guild]["watch_mode"]:
            await self.log_message(message, "Deletion")


async def setup(bot: "PeterBot") -> None:
    await bot.add_cog(OnHandling(bot))
