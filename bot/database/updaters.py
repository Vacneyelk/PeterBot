from typing import TYPE_CHECKING

from database import writers

from asyncpg import Connection

if TYPE_CHECKING:
    from peterbot import PeterBot


async def update_guild_watch(bot: "PeterBot", guild_id: int, watch_mode: bool) -> None:
    """
    Updates the watch mode in the database for a guild

    Parameters
    ----------
    bot : PeterBot
    guild_id : int
        the snowflake id of the guild
    watch_mode : bool
        boolean flag for whether the bot should be logging messages

    Returns
    -------
    None
    """
    if guild_id not in bot.peter_guilds:
        await writers.insert_guild(bot, guild_id)
    async with bot.db_pool.acquire() as conn:
        conn: Connection
        async with conn.transaction():
            await conn.execute(
                "UPDATE guilds SET watch_mode = $1 " "WHERE guild_id = $2 ",
                watch_mode,
                guild_id,
            )
    bot.peter_guilds[guild_id]["watch_mode"] = watch_mode
