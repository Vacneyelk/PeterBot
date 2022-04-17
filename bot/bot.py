import os

import discord
from discord.ext import commands

initial_cogs = ("cogs.utilities",)

bot_owner = os.environ["OWNER_ID"]


def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f"<@!{user_id}>", f"<@{user_id}>", "$"]
    return base


class PeterBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents().all()
        super().__init__(
            command_prefix=_prefix_callable, intents=intents, owner_id=bot_owner
        )

    async def setup_hook(self):
        for cog in initial_cogs:
            print(f"loading cog {cog}...")
            await self.load_extension(cog)

    async def on_ready(self):
        print(f"{self.user} online (ID: {self.user.id}")
        print("-" * 88)

        activity = discord.Game("Watching over the anthill")
        await self.change_presence(status=discord.Status.online, activity=activity)


changed = None
