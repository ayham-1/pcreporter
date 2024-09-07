import traceback
import logging
import os

import asyncio

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("pcreporter")

from telegram import ForceReply, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from pcreporter.info.overview import info_overview
from pcreporter.info.temp import info_temp
from pcreporter.info.usb import info_usb

from pcreporter.monitor.usb import monitor_usb_start, monitor_usb_stop

from pcreporter.fn.lock_screen import fn_lock_screen


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
    "overview": cmd_overview,
    "ping": cmd_overview,
    "temp": cmd_temp,
    "usb": cmd_usb,
    "lockscrn": cmd_fn_lock_screen,
}
keyboard = [[]]


def get_cmds_keyboard():
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


async def __main():
    if not good_permissions():
        logger.error("Invalid permissions, ensure normal user permissions")
        exit(1)

    token = os.getenv("TELEGRAM_TOKEN")
    if token is None:
        logger.error("TELEGRAM_TOKEN is not set")
        return

    state.read_config()

    # add rows of three to keyboard
    for cmd in cmds.keys():
        if len(keyboard[-1]) == 3:
            keyboard.append([])

        keyboard[-1].append("/" + cmd)

    application = ApplicationBuilder().token(token).build()
    await application.initialize()
    application.add_error_handler(error_handler)

    for cmd, handler in cmds.items():
        application.add_handler(CommandHandler(cmd, handler))

    try:
        import socket

        monitor_usb_start(application.bot)
        await application.bot.send_message(
            state.CHAT_ID, f"Hello, reporting as {socket.gethostname()}"
        )

        await application.bot.send_message(
            state.CHAT_ID, "Select an option", reply_markup=get_cmds_keyboard()
        )

        await asyncio.gather(
            run_polling(application),  # Run the bot polling
        )
        monitor_usb_stop()
    except KeyboardInterrupt:
        logger.info("Recieved Ctrl + C. Shutting down...")
    finally:
        await application.bot.send_message(
            state.CHAT_ID, "Farewell, bot is shutting down"
        )
        logger.info("Shut down")
        exit(0)


def main():
    asyncio.run(__main())
