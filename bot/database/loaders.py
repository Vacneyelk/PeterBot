from collections import defaultdict
from typing import TYPE_CHECKING, Mapping

if TYPE_CHECKING:
    from peterbot import PeterBot


async def request_guilds(bot: "PeterBot") -> Mapping[str, Mapping[str, bool]]:
    """
    Builds a dictionary of guild data that the bot exists in

    Parameters
    ----------
    bot : PeterBot

    Returns
    -------
    dict
        Dictionary of guild id and its associated data

        {
            'guild_id' : {
                'watch_mode' : bool
            }, ...
        }
    """
    async with bot.db_pool.acquire() as conn:
        query = await conn.prepare("SELECT * FROM guilds")
        results = defaultdict(dict)

        for row in await query.fetch():
            results[row["guild_id"]]["watch_mode"] = row["watch_mode"]
    return results
