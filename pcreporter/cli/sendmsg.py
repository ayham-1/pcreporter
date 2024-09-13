import asyncio
import logging

import pcreporter.state as state

logger = logging.getLogger("pcreporter")

__bot = None
__loop = None

def send_msg_init(bot, loop):
    global __bot, __loop
    __bot = bot
    __loop = loop



def send_msg_safe(msg, **kwargs):
    global __bot, __loop
    assert __bot is not None and __loop is not None, "send_msg_init not called"

    if state.CHAT_ID == None:
        logger.error("CHAT_ID is not set in the config file, could not send message")
        return

    try:
        asyncio.run_coroutine_threadsafe(__send_msg(msg, **kwargs), __loop)
    except Exception as e:
        logger.error(f"Error sending message: {e}")

async def __send_msg(msg, **kwargs):
    global __bot, __loop
    assert __bot is not None and __loop is not None, "send_msg_init not called"

    try:
        await __bot.send_message(state.CHAT_ID, msg, **kwargs)
    except Exception as e:
        logger.error(f"Error sending message: {e}")
