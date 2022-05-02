import os

import asyncpg
import discord
from database import loaders, writers
from discord.ext import commands

initial_cogs = ("cogs.utilities", "cogs.schedule")

bot_owner = os.environ["OWNER_ID"]
db_user = os.environ["POSTGRES_USER"]
db_password = os.environ["POSTGRES_PASSWORD"]
db_host = os.environ["POSTGRES_HOST"]
db_port = os.environ["POSTGRES_PORT"]
db_database = os.environ["POSTGRES_DB"]


def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f"<@!{user_id}>", f"<@{user_id}>", "$"]
    return base


class PeterBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents().all()
        application_id = int(os.environ["APPLICATION_ID"])
        super().__init__(
            command_prefix=_prefix_callable,
            intents=intents,
            owner_id=bot_owner,
            application_id=application_id,
        )

    async def setup_hook(self):
        """
        Setup hook is used to initialize the bot before handling any events

        Functional override of discord.Client.setup_hook
        """
        # Load cogs
        for cog in initial_cogs:
            print(f"loading cog {cog}...")
            await self.load_extension(cog)
        # create database connection pools
        self.db_pool = await asyncpg.create_pool(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database=db_database,
        )
        # Load caches
        # Certain tables are cached to avoid making calls to the database
        self.peter_guilds = await loaders.request_guilds(self)
        self.peter_users = await loaders.request_users(self)
        self.peter_channels = await loaders.request_channels(self)
        self.peter_voice_channels = await loaders.request_voice_channels(self)
        self.peter_catalogue_aliases = await loaders.request_catalogue_aliases(self)
        # Add new guilds
        async for guild in self.fetch_guilds(limit=None):
            if guild.id not in self.peter_guilds:
                await writers.insert_guild(self, guild.id)

        for guild_id in self.peter_guilds.keys():
            self.tree.copy_global_to(guild=discord.Object(id=guild_id))
            await self.tree.sync(guild=discord.Object(id=guild_id))
        await self.tree.sync()

    async def on_ready(self):
        print(f"{self.user} online (ID: {self.user.id})")
        print("-" * 88)

        activity = discord.Game("Watching over the anthill")
        await self.change_presence(status=discord.Status.online, activity=activity)

    async def on_guild_join(self, guild):
        if guild.id not in self.peter_guilds:
            await writers.insert_guild(self, guild.id)
