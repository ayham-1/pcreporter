import traceback
import logging
import os

import asyncio

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("pcreporter")

from telegram import (
    ForceReply,
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from pcreporter.info.overview import info_overview
from pcreporter.info.temp import info_temp
from pcreporter.info.usb import info_usb

from pcreporter.monitor.usb import monitor_usb_start, monitor_usb_stop

from pcreporter.fn.lock_screen import fn_lock_screen
from pcreporter.fn.shutdown import fn_shutdown


import pcreporter.state as state


async def cmd_overview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the overview message when the command /overview is issued."""
    if update.message is None:
        return
    await update.message.reply_html(info_overview(), reply_markup=get_cmds_keyboard())


async def cmd_temp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the temp message when the command /overview is issued."""
    if update.message is None:
        return
    await update.message.reply_html(info_temp(), reply_markup=get_cmds_keyboard())


async def cmd_usb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the overview message when the command /usb is issued."""
    if update.message is None:
        return
    await update.message.reply_html(info_usb(), reply_markup=get_cmds_keyboard())


async def cmd_defensive_enable(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message is None:
        return
    state.IS_DEFENSIVE = True
    await update.message.reply_html(
        "Defensive mode enabled, current state: " + str(state.IS_DEFENSIVE),
        reply_markup=get_cmds_keyboard(),
    )


async def cmd_defensive_disable(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message is None:
        return
    state.IS_DEFENSIVE = False
    await update.message.reply_html(
        "Defensive mode disabled, current state: " + str(state.IS_DEFENSIVE),
        reply_markup=get_cmds_keyboard(),
    )


async def cmd_fn_lock_screen(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message is None:
        return
    await update.message.reply_html(fn_lock_screen(), reply_markup=get_cmds_keyboard())


ASKING_SHUTDOWN = False


async def cmd_fn_shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await update.message.reply_html(
        "Are you sure you want to shutdown the system?",
        reply_markup=ReplyKeyboardMarkup([["Yes", "No"]]),
    )
    global ASKING_SHUTDOWN
    ASKING_SHUTDOWN = True


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    global ASKING_SHUTDOWN
    if ASKING_SHUTDOWN and update.message.text == "Yes":
        await update.message.reply_html(fn_shutdown(), reply_markup=get_cmds_keyboard())
        return
    elif ASKING_SHUTDOWN and update.message.text == "No":
        await update.message.reply_html(
            "Shutdown cancelled", reply_markup=get_cmds_keyboard()
        )
    else:
        await update.message.reply_text(
            "I'm sorry, I didn't understand that command. Please try again.",
            reply_markup=get_cmds_keyboard(),
        )


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


cmds = {
    "defensive": cmd_defensive_enable,
    "observe": cmd_defensive_disable,
    "ping": cmd_overview,
    "temp": cmd_temp,
    "usb": cmd_usb,
    "lockscrn": cmd_fn_lock_screen,
    "shutdown": cmd_fn_shutdown,
}
keyboard = [[]]


def get_cmds_keyboard():
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


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

    await echo(update, context)

async def safe_send_msg(app, msg, **kwargs):
    if state.CHAT_ID != None:
        await app.bot.send_message(state.CHAT_ID, msg, **kwargs)


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

    for cmd in cmds.keys():
        if len(keyboard[-1]) % 3 == 0:
            keyboard.append([])

        keyboard[-1].append("/" + cmd)

    application = ApplicationBuilder().token(state.TOKEN).build()
    await application.initialize()
    application.add_error_handler(error_handler)

    application.add_handler(
        MessageHandler(filters.ALL, restricted_handler)
    )

    try:
        import socket

        monitor_usb_start(application.bot)

        await safe_send_msg(application, f"Hello, reporting as {socket.gethostname()}")
        await safe_send_msg(application, "Select an option", reply_markup=get_cmds_keyboard())

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
