from collections import defaultdict
from typing import TYPE_CHECKING, Mapping, Set

from asyncpg import Connection

if TYPE_CHECKING:
    from peterbot import PeterBot


async def request_guilds(bot: "PeterBot") -> Mapping[int, Mapping[str, bool]]:
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
            guild_id : {
                'watch_mode' : bool
            }, ...
        }
    """
    results = defaultdict(dict)
    async with bot.db_pool.acquire() as conn:
        conn: Connection
        query = await conn.prepare("SELECT * FROM guilds")
        for row in await query.fetch():
            results[row["guild_id"]]["watch_mode"] = row["watch_mode"]
    return results


async def request_users(bot: "PeterBot") -> Mapping[int, Set[int]]:
    """
    Builds a dictionary of user data by build

    Parameters
    ----------
    bot : PeterBot

    Returns
    -------
    dict
        Dictionary of users registered to a guild

        {
            guild_id : {user_id_1, user_id_2, ...}, ...
        }
    """
    results = defaultdict(set)
    async with bot.db_pool.acquire() as conn:
        conn: Connection
        query = await conn.prepare("SELECT * FROM users")
        for row in await query.fetch():
            results[row["guild_id"]].add(row["user_id"])
    return results


async def request_catalogue_aliases(bot: "PeterBot") -> Mapping[int, Mapping[str, str]]:
    """
    Builds a dictionary of catalogue aliases by guild id

    Parameters
    ----------
    bot : PeterBot

    Returns
    -------
    dict
        Dictionary of catalogue aliases registered to a guild

        {
            guild_id : {
                'alias' : 'department', ...
            }, ...
        }
    """
    results = defaultdict(dict)
    async with bot.db_pool.acquire() as conn:
        conn: Connection
        query = await conn.prepare("SELECT * FROM catalogue_alias")
        for row in await query.fetch():
            results[row["guild_id"]][row["alias"]] = row["department"]
    return results


async def request_channels(bot: "PeterBot") -> Mapping[int, Set[int]]:
    """
    Builds a dictionary of channels by guild id

    Parameters
    ----------

    Returns
    -------
    dict
        Dictionary of channels registered to a guild

        {
            guild_id : {channel_id_1, channel_id_2, ...}, ...
        }
    """
    results = defaultdict(set)
    async with bot.db_pool.acquire() as conn:
        conn: Connection
        query = await conn.prepare("SELECT * FROM channels")
        for row in await query.fetch():
            results[row["guild_id"]].add(row["channel_id"])
    return results


async def request_voice_channels(
    bot: "PeterBot",
) -> Mapping[int, Mapping[int, Mapping[str, str]]]:
    """
    Builds a dictionary of managed voice channels by guild id

    Parameters
    ----------
    bot : PeterBot

    Returns
    -------
    dict
        Dictionary of managed voice channels to a guild

        {
            guild_id : {
                voice_channel_id : {
                    'text_id' : text_id,
                    'role_id' : role_id
                }
            }
        }
    """
    results = defaultdict(dict)
    async with bot.db_pool.acquire() as conn:
        conn: Connection
        query = await conn.prepare("SELECT * FROM voice_channels")
        for row in await query.fetch():
            guild_id = row["guild_id"]
            voice_id = row["voice_id"]
            results[guild_id] = {}
            results[guild_id][voice_id]["text_id"] = row["text_id"]
            results[guild_id][voice_id]["role_id"] = row["role_id"]
    return results
