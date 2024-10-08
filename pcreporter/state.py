import os
import sys
import platform
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("pcreporter")

this = sys.modules[__name__]

CHAT_ID = None
IS_DEFENSIVE = False
CMD_LOCKSCRN = None
TOKEN = None


def read_config():
    """Read configuration file into self."""
    conf_to_read = None

    if not platform.system() == "Windows":
        if os.path.exists("/etc/pcreporter.conf"):
            conf_to_read = "/etc/pcreporter.conf"
        elif os.path.exists(
            os.path.expanduser("~/.config/pcreporter.conf")
        ):
            conf_to_read = os.path.expanduser("~/.config/pcreporter.conf")
        elif os.path.exists(
            os.path.expanduser("~/.pcreporter.conf")
        ):
            conf_to_read = os.path.expanduser("~/.pcreporter.conf")
    elif platform.system() == "Windows" and os.path.exists(
        os.path.join(os.environ["APPDATA"], "pcreporter.conf")
    ):
        conf_to_read = os.path.join(os.environ["APPDATA"], "pcreporter.conf")

    if conf_to_read == None and os.path.exists("pcreporter.conf"):
        conf_to_read = "pcreporter.conf"
    elif conf_to_read == None:
        raise FileNotFoundError(f"No configuration file not found.")

    with open(conf_to_read, "r") as f:
        line_num = 1
        for line in f.readlines():
            if not "=" in line:
                logger.error(
                    f"Error reading configuration file {conf_to_read}: Line {line_num} does not contain '='."
                )
                continue

            line = line.split("=")
            if len(line) != 2:
                logger.error(
                    f"Error reading configuration file {conf_to_read}: Line {line_num} must only contain one '=' ."
                )
                continue

            global CHAT_ID, IS_DEFENSIVE, CMD_LOCKSCRN, TOKEN
            if line[0] == "CHAT_ID":
                CHAT_ID = int(line[1])
            if line[0] == "IS_DEFENSIVE":
                if line[1].strip() == "false":
                    IS_DEFENSIVE = False
                else:
                    IS_DEFENSIVE = True
            if line[0] == "CMD_LOCKSCRN":
                CMD_LOCKSCRN = line[1].strip()
            if line[0] == "TOKEN":
                TOKEN = line[1].strip()

            line_num += 1
