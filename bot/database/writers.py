from typing import TYPE_CHECKING

from asyncpg import Connection

if TYPE_CHECKING:
    from peterbot import PeterBot


async def insert_guild(
    bot: "PeterBot", guild_id: int, watch_mode: bool = False
) -> None:
    """
    Adds a new guild to the database and updates bot.peter_guilds

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
