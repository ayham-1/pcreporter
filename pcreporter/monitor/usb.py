import asyncio

from usbmonitor import USBMonitor
from usbmonitor.attributes import ID_MODEL, ID_MODEL_ID, ID_VENDOR_ID

import pcreporter.state as state

monitor = None
telegram_bot = None

device_info_str = (
    lambda device_info: f"{device_info[ID_MODEL]} ({device_info[ID_MODEL_ID]} - {device_info[ID_VENDOR_ID]})"
)


def on_connect(device_id, device_info):
    assert not state is None
    if not telegram_bot or not state.CHAT_ID:
        return

    try:
        asyncio.run(
            telegram_bot.send_message(
                state.CHAT_ID,
                "Detected new USB connection: "
                + device_info_str(device_info=device_info),
            )
        )
    except Exception as _:
        pass


def on_disconnect(device_id, device_info):
    assert not state is None
    if not telegram_bot or not state.CHAT_ID:
        return

    try:
        asyncio.run(
            telegram_bot.send_message(
                state.CHAT_ID,
                "Detected USB disconnection: "
                + device_info_str(device_info=device_info),
            )
        )
    except Exception as _:
        pass


def monitor_usb_start(bot):
    global monitor, telegram_bot
    telegram_bot = bot

    # Create the USBMonitor instance
    monitor = USBMonitor()

    # Start the daemon
    monitor.start_monitoring(on_connect=on_connect, on_disconnect=on_disconnect)


def monitor_usb_stop():
    if not monitor:
        return

    monitor.stop_monitoring()
