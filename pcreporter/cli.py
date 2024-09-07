import traceback
import logging
import os

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("pcreporter")

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes

from pcreporter.info.overview import info_overview
from pcreporter.info.temp import info_temp
from pcreporter.info.usb import info_usb

from pcreporter.monitor.usb import monitor_usb_start, monitor_usb_stop

from pcreporter.fn.lock_screen import fn_lock_screen


import pcreporter.state as state


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user

    if update.message is None or user is None:
        return

    # state.__CHAT_ID__ = update.message.chat_id
    # logger.info(f"state.__CHAT_ID__: {state.__CHAT_ID__}")

    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def cmd_overview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the overview message when the command /overview is issued."""
    if update.message is None:
        return
    await update.message.reply_html(info_overview())


async def cmd_temp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the temp message when the command /overview is issued."""
    if update.message is None:
        return
    await update.message.reply_html(info_temp())


async def cmd_usb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the overview message when the command /usb is issued."""
    if update.message is None:
        return
    await update.message.reply_html(info_usb())


async def cmd_defensive_enable(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message is None:
        return
    state.IS_DEFENSIVE = True
    await update.message.reply_html(
        "Defensive mode enabled, current state: " + str(state.IS_DEFENSIVE)
    )


async def cmd_defensive_disable(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message is None:
        return
    state.IS_DEFENSIVE = False
    await update.message.reply_html(
        "Defensive mode disabled, current state: " + str(state.IS_DEFENSIVE)
    )


async def cmd_fn_lock_screen(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.message is None:
        return
    await update.message.reply_html(fn_lock_screen())


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


def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.

    token = os.getenv("TELEGRAM_TOKEN")
    if token is None:
        logger.error("TELEGRAM_TOKEN is not set")
        return

    state.read_config()
    application = Application.builder().token(token).build()
    application.add_error_handler(error_handler)

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("defensive", cmd_defensive_enable))
    application.add_handler(CommandHandler("observe", cmd_defensive_disable))

    application.add_handler(CommandHandler("overview", cmd_overview))
    application.add_handler(CommandHandler("ping", cmd_overview))
    application.add_handler(CommandHandler("temp", cmd_temp))
    application.add_handler(CommandHandler("usb", cmd_usb))
    application.add_handler(CommandHandler("lockscrn", cmd_fn_lock_screen))

    # Run the bot until the user presses Ctrl-C
    logger.warn("Message the bot with /start to get started")

    monitor_usb_start(application.bot)
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    monitor_usb_stop()
