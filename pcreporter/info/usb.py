from usbmonitor import USBMonitor
from usbmonitor.attributes import ID_MODEL, ID_MODEL_ID, ID_VENDOR_ID


def info_usb():
    # Create the USBMonitor instance
    monitor = USBMonitor()

    # Get the current devices
    devices_dict = monitor.get_available_devices()

    result_str = "<b>USB Devices:</b>\n"
    for device_id, device_info in devices_dict.items():
        result_str += f"{device_id} -- {device_info[ID_MODEL]} ({device_info[ID_MODEL_ID]} - {device_info[ID_VENDOR_ID]})\n"

    return result_str
