import traceback
import logging
import os

import asyncio

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("pcreporter")

from telegram import (
    Update,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    MessageHandler,
    ApplicationBuilder,
    ContextTypes,
    filters,
)

from pcreporter.monitor.usb import monitor_usb_start, monitor_usb_stop

import pcreporter.state as state

from pcreporter.cli.sendmsg import *
from pcreporter.cli.cmds import *


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    if context is None:
        return

    logger.error("Exception while handling an update:", exc_info=context.error)

    assert context.error
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )

    tb_string = "".join(tb_list)
    logger.error(tb_string)


def good_permissions():
    return not os.getuid() == 0  # windows sucks haha


async def run_polling(application):
    """Imitate the behavior of application.run_polling()."""
    # Start polling
    await application.start()
    logger.info("Polling started...")

    # Keep the bot running until it is stopped
    try:
        await application.updater.start_polling()  # Start polling for updates
        await asyncio.Event().wait()  # Run indefinitely
    finally:
        # Gracefully shut down the bot
        await application.updater.stop()
        await application.stop()
        logger.info("Polling stopped...")


async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return False
    if update.message.chat_id == state.CHAT_ID:
        return True

    await update.message.reply_text(
        f"You are not authorized to use this bot.\nIf this is your bot, please set the CHAT_ID in the config file to your chat id, {update.message.chat_id}."
    )

    return False

async def restricted_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    if not await is_authorized(update, context):
        logger.warn(f"Unauthorized access from chat ID: {update.message.chat_id}")
        return

    msg = update.message.text
    if msg is None:
        return
    msg = msg[1:].lower().strip()

    logger.info(f"handling /{msg} from: {update.message.chat_id}")
    for cmd, handler in cmds.items():
        if msg.startswith(cmd):
            await handler(update, context)
            return

    await lump_handler(update, context)

async def __main():
    if not good_permissions():
        logger.error("Invalid permissions, ensure normal user permissions")
        exit(1)

    state.read_config()

    if state.TOKEN is None:
        state.TOKEN = os.getenv("TELEGRAM_TOKEN")

    if state.TOKEN is None:
        logger.error("TELEGRAM_TOKEN is not set nor in config file")
        return

    cmds_keyboard_init()

    application = ApplicationBuilder().token(state.TOKEN).build()
    await application.initialize()
    application.add_error_handler(error_handler)

    application.add_handler(
        MessageHandler(filters.ALL, restricted_handler)
    )

    try:
        import socket

        monitor_usb_start(application.bot)
        send_msg_init(application.bot, asyncio.get_event_loop())

        send_msg_safe(f"Hello, reporting as {socket.gethostname()}")
        send_msg_safe("Select an option", reply_markup=get_cmds_keyboard())

        await asyncio.gather(
            run_polling(application),
        )
        monitor_usb_stop()
    except KeyboardInterrupt:
        logger.info("Recieved Ctrl + C. Shutting down...")
    finally:
        if state.CHAT_ID != None:
            await application.bot.send_message(
                state.CHAT_ID, "Farewell, bot is shutting down"
            )
        logger.info("Shut down")
        exit(0)


def main():
    asyncio.run(__main())
