import logging
import os

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes

import pcreporter.state as state
from pcreporter.info.overview import info_overview
from pcreporter.info.usb import info_usb
from pcreporter.monitor.usb import monitor_usb_start, monitor_usb_stop

user_chat_id = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user

    if update.message is None or user is None:
        return

    state.__CHAT_ID__ = update.message.chat_id
    logger.info(f"state.__CHAT_ID__: {state.__CHAT_ID__}")

    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def cmd_overview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the overview message when the command /overview is issued."""
    if update.message is None:
        return
    await update.message.reply_html(info_overview())


async def cmd_usb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the overview message when the command /usb is issued."""
    if update.message is None:
        return
    await update.message.reply_html(info_usb())


def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.

    token = os.getenv("TELEGRAM_TOKEN")

    if token is None:
        logger.error("TELEGRAM_TOKEN is not set")
        return

    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("overview", cmd_overview))
    application.add_handler(CommandHandler("ping", cmd_overview))

    application.add_handler(CommandHandler("usb", cmd_usb))

    # Run the bot until the user presses Ctrl-C
    logger.warn("Message the bot with /start to get started")

    monitor_usb_start(application.bot)
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    monitor_usb_stop()
