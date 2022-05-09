from datetime import datetime
from typing import TYPE_CHECKING, Literal

from asyncpg import Connection

if TYPE_CHECKING:
    from peterbot import PeterBot


async def insert_guild(
    bot: "PeterBot", guild_id: int, watch_mode: bool = False
) -> None:
    """
    Adds a new guild to the database and updates bot.peter_guilds
    TODO: should add a ON CONFLICT DO NOTHING clause

    Parameters
    ----------
    bot : PeterBot
    guild_id : int
        the snowflake id of the guild
    watch_mode : bool
        boolean for whether to log messages

    Returns
    -------
    None
    """
    async with bot.db_pool.acquire() as conn:
        conn: Connection
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO guilds VALUES ($1, $2)", guild_id, watch_mode
            )
    bot.peter_guilds[guild_id]["watch_mode"] = watch_mode


async def insert_user(bot: "PeterBot", guild_id: int, user_id: int) -> None:
    """
    Adds a new user to a guild and updates bot.peter_users
    TODO: should add a ON CONFLICT DO NOTHING clause

    Parameters
    ----------
    bot : PeterBot
    guild_id : int
        snowflake id of the guild
    user_id : int
        snowflake id of the user

    Returns
    -------
    None
    """
    async with bot.db_pool.acquire() as conn:
        conn: Connection
        async with conn.transaction():
            await conn.execute("INSERT INTO users VALUES ($1, $2)", user_id, guild_id)
        bot.peter_users[guild_id].add(user_id)


async def insert_catalogue_alias(
    bot: "PeterBot", guild_id: int, alias: str, department: str
) -> None:
    """
    Adds a new alias for a department and updates bot.peter_catalogue_aliases

    Parameters
    ----------
    bot : PeterBot
    guild_id : int
        snowflake id of the guild
    alias : str
        given alias for a department
    department : str
        given department

    Returns
    -------
    None
    """
    async with bot.db_pool.acquire() as conn:
        conn: Connection
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO catalogue_alias VALUES ($1, $2, $3)",
                guild_id,
                department,
                alias,
            )
        bot.peter_catalogue_aliases[guild_id][alias] = department


async def insert_channel(bot: "PeterBot", guild_id: int, channel_id: int) -> None:
    """
    Adds a new channel and updates bot.peter_channels
    TODO: should add a ON CONFLICT DO NOTHING clause

    Parameters
    ----------
    bot : PeterBot
    guild_id : int
        snowflake id of the guild
    channel_id : int
        snowflake id of the channel

    Returns
    -------
    None
    """
    async with bot.db_pool.acquire() as conn:
        conn: Connection
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO channels VALUES ($1, $2)", channel_id, guild_id
            )
        bot.peter_channels[guild_id].add(channel_id)


async def insert_voice_channel(
    bot: "PeterBot", guild_id: int, voice_id: int, text_id: int, role_id: int
) -> None:
    """
    Adds a new managed voice channel

    Parameters
    ----------
    bot : PeterBot
    guild_id : int
        snowflake id for the guild
    voice_id : int
        snowflake id for the voice channel
    text_id : int
        snowflake id for the text channel
    role_id : int
        snowflake id for the voice role

    Returns
    -------
    None
    """
    async with bot.db_pool.acquire() as conn:
        conn: Connection
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO voice_channels VALUES ($1, $2, $3, $4)",
                voice_id,
                guild_id,
                text_id,
                role_id,
            )
        bot.peter_voice_channels[guild_id][voice_id] = {}
        bot.peter_voice_channels[guild_id][voice_id]["text_id"] = text_id
        bot.peter_voice_channels[guild_id][voice_id]["role_id"] = role_id


MESSAGE_TYPE = Literal["Original", "Edit: before", "Edit: after", "Deletion"]


async def insert_user_message(
    bot: "PeterBot",
    guild_id: int,
    channel_id: int,
    user_id: int,
    message_id: int,
    message: str,
    message_type: MESSAGE_TYPE,
    message_date: datetime,
) -> None:
    """
    Adds a new user message to the database. If the guild, user, or channel of the
    message doesn't exist in the database, it's added

    Parameters
    ----------
    bot : PeterBot
    guild_id : int
        snowflake id of the guild
    channel_id : int
        snowflake id of the channel
    user_id : int
        snowflake id of the user
    message_id : int
        snowflake id of the message
    message : str
        message content
    message_type : str
        message type `[Original, Edit: before, Edit: after, Deletion]`
    message_date : datetime
        message timestamp

    Returns
    -------
    None
    """
    message_date = message_date.replace(tzinfo=None)
    # check if the foreign keys exist in the DB and insert
    if guild_id not in bot.peter_guilds:
        await insert_guild(bot, guild_id)
    if channel_id not in bot.peter_channels[guild_id]:
        await insert_channel(bot, guild_id, channel_id)
    if user_id not in bot.peter_users[guild_id]:
        await insert_user(bot, guild_id, user_id)
    async with bot.db_pool.acquire() as conn:
        conn: Connection
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO user_logs VALUES ($1, $2, $3, $4, $5, $6, $7)",
                user_id,
                channel_id,
                guild_id,
                message_id,
                message,
                message_type,
                message_date,
            )
