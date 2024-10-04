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

from pcreporter.info.overview import info_overview
from pcreporter.info.temp import info_temp
from pcreporter.info.usb import info_usb
from pcreporter.info.programs import info_programs

from pcreporter.fn.lock_screen import fn_lock_screen
from pcreporter.fn.shutdown import fn_shutdown
from pcreporter.fn.tailscale import fn_tailscale_up, fn_tailscale_down, fn_tailscale_status

import pcreporter.state as state

async def cmd_overview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await update.message.reply_html(info_overview(), reply_markup=get_cmds_keyboard())


async def cmd_temp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await update.message.reply_html(info_temp(), reply_markup=get_cmds_keyboard())


async def cmd_usb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await update.message.reply_html(info_usb(), reply_markup=get_cmds_keyboard())

async def cmd_programs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await update.message.reply_html(info_programs(), reply_markup=get_cmds_keyboard())

async def cmd_tailscale(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await update.message.reply_html(
        "Call a command from the tailscale commands", reply_markup=get_tailscale_keyboard()
    )

async def cmd_tailscale_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await update.message.reply_html(
        "Closed tailscale commands panel", reply_markup=get_cmds_keyboard()
    )

        
async def cmd_tailscale_up(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await update.message.reply_html(str(fn_tailscale_up()), reply_markup=get_tailscale_keyboard())

async def cmd_tailscale_down(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await update.message.reply_html(str(fn_tailscale_down()), reply_markup=get_tailscale_keyboard())

async def cmd_tailscale_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await update.message.reply_html(str(fn_tailscale_status()), reply_markup=get_tailscale_keyboard())


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


async def lump_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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


cmds = {
    "defensive": cmd_defensive_enable,
    "observe": cmd_defensive_disable,
    "ping": cmd_overview,
    "temp": cmd_temp,
    "usb": cmd_usb,
    "programs": cmd_programs,
    "tailscale": cmd_tailscale,
    "lockscrn": cmd_fn_lock_screen,
    "shutdown": cmd_fn_shutdown,
}
cmds_tailscale = {
    "up": cmd_tailscale_up,
    "down": cmd_tailscale_down,
    "status": cmd_tailscale_status,
    "back": cmd_tailscale_back,
}
keyboard = [[]]
keyboard_tailscale = [[]]


def get_cmds_keyboard():
    global keyboard
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_tailscale_keyboard():
    global keyboard_tailscale
    return ReplyKeyboardMarkup(keyboard_tailscale, resize_keyboard=True, one_time_keyboard=False)

def cmds_keyboard_init():
    global keyboard
    for cmd in cmds.keys():
        if len(keyboard[-1]) % 3 == 0:
            keyboard.append([])

        keyboard[-1].append("/" + cmd)

    global keyboard_tailscale
    for cmd in cmds_tailscale.keys():
        if len(keyboard_tailscale[-1]) % 3 == 0:
            keyboard_tailscale.append([])

        keyboard_tailscale[-1].append("/" + cmd)
