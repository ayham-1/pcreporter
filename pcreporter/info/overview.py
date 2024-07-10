import platform
import re
import socket
import time
import uuid

import psutil
import uptime
from requests import get


def info_overview():
    _os = platform.system()
    _os_version = platform.version()
    _hostname = socket.gethostname()
    _local_ip = socket.gethostbyname(_hostname)
    _public_ip = get("https://api.ipify.org").text
    _mac = ":".join(re.findall("..", "%012x" % uuid.getnode()))

    _total_ram = None
    _used_ram = None
    _available_ram = None
    _percentage_ram = None
    try:
        ram_info = psutil.virtual_memory()
        _total_ram = f"{ram_info.total / (1024 ** 3): .2f} GB"
        _used_ram = f"{ram_info.used / (1024 ** 3): .2f} GB"
        _available_ram = f"{ram_info.available / (1024 ** 3): .2f} GB"
        _percentage_ram = f"{ram_info.percent}%"
    except Exception as e:
        print("could not get RAM info: {}", e)

    _uptime = uptime.uptime()
    # convert uptime to readable format with days, hours, minutes, seconds
    _uptime = time.strftime(
        "%d days, %H hours, %M minutes, %S seconds", time.gmtime(_uptime)
    )

    return f"""
<b>Reporting as {_hostname}</b>

Uptime: {_uptime}

OS: {_os}
OS Version: {_os_version}
Local IP Address: {_local_ip}
Public IP Address: {_public_ip}
MAC Address: {_mac}

Total RAM: {_total_ram}
Used RAM: {_used_ram}
Available RAM: {_available_ram}
Percentage RAM Used: {_percentage_ram}
    """
