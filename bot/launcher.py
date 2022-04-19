import asyncio
import os

from peterbot import PeterBot

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

bot_token = os.environ["BOT_TOKEN"]


def run_bot():
    bot: PeterBot = PeterBot()
    bot.run(bot_token)


if __name__ == "__main__":
    run_bot()
