import sys
import logging
import asyncio

from usbmonitor import USBMonitor
from usbmonitor.attributes import ID_MODEL, ID_MODEL_ID, ID_VENDOR_ID

import pcreporter.state as state

from pcreporter.cli.sendmsg import send_msg_safe

logger = logging.getLogger("pcreporter")

monitor = None
telegram_bot = None

device_info_str = (
    lambda device_info: f"{device_info[ID_MODEL]} ({device_info[ID_MODEL_ID]} - {device_info[ID_VENDOR_ID]})"
)


def __usb_defensive():
    logger.warn("Defensive mode enabled\nUSB change detected, shutting down...")
    if sys.platform == "win32":
        import ctypes

        user32 = ctypes.WinDLL("user32")
        user32.ExitWindowsEx(0x00000008, 0x00000000)
    else:
        import os

        os.system("systemctl poweroff")

    exit(1)


def __usb_on_connect(device_id, device_info):
    assert not state is None
    if not telegram_bot or not state.CHAT_ID:
        return

    send_msg_safe(f"Detected new USB connection: {device_info_str(device_info=device_info)}, {device_id}")
    if state.IS_DEFENSIVE:
        send_msg_safe("Defensive mode enabled, shutting down...")
        __usb_defensive()

def __usb_on_disconnect(device_id, device_info):
    assert not state is None
    if not telegram_bot or not state.CHAT_ID:
        return

    send_msg_safe(f"Detected USB disconnection: {device_info_str(device_info=device_info)}, {device_id}")
    if state.IS_DEFENSIVE:
        send_msg_safe("Defensive mode enabled, shutting down...")
        __usb_defensive()


def monitor_usb_start(bot):
    global monitor, telegram_bot
    telegram_bot = bot

    # Create the USBMonitor instance
    monitor = USBMonitor()

    # Start the daemon
    monitor.start_monitoring(
        on_connect=__usb_on_connect, on_disconnect=__usb_on_disconnect
    )


def monitor_usb_stop():
    if not monitor:
        return

    monitor.stop_monitoring()
