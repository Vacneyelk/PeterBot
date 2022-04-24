from typing import TYPE_CHECKING, Any, List, Mapping

from asyncpg import Connection

if TYPE_CHECKING:
    from peterbot import PeterBot


async def get_user_logs(
    bot: "PeterBot", guild_id: int, user_id: int
) -> List[Mapping[str, Any]]:
    """
    Retrieve a list of user log data

    Parameters
    ----------
    bot : PeterBot
    guild_id : int
        snowflake id of guild we want logs from
    user_id : int
        snowflake id of user we want logs from

    Returns
    -------
    list
        a list of dictionary objects containing message data

        [
            {
                'guild_id' : int,
                'user_id' : int,
                'message_id' : int,
                'message' : str,
                'message_type' : str,
                'message_date' : datetime
            }, ...
        ]
    """
    results: list
    async with bot.db_pool.acquire() as conn:
        conn: Connection
        query = await conn.prepare(
            "SELECT * FROM user_logs ",
            "WHERE guild_id = $1 AND user_id = $2 ",
            "ORDER BY msg_date DESC",
        )
        results = [
            {
                "guild_id": row["guild_id"],
                "user_id": row["user_id"],
                "message_id": row["mesage_id"],
                "message": row["msg"],
                "message_type": row["msg_type"],
                "message_date": row["msg_date"],
            }
            for row in await query.fetch(guild_id, user_id)
        ]
    return results
