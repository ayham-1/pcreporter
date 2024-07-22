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


def read_config():
    """Read configuration file into self."""
    global CHAT_ID, IS_DEFENSIVE
    conf_to_read = None

    if not platform.system() == "Windows":
        if os.path.exists("/etc/pcreporter/pcreporter.conf"):
            conf_to_read = "/etc/pcreporter/pcreporter.conf"
        elif os.path.exists(
            os.path.join(os.environ["XDG_CONFIG_HOME"], "pcreporter.conf")
        ):
            conf_to_read = os.path.join(
                os.environ["XDG_CONFIG_HOME"], "pcreporter.conf"
            )
        elif os.path.exists(os.path.join(os.environ["HOME"], ".pcreporter.conf")):
            conf_to_read = os.path.join(os.environ["HOME"], ".pcreporter.conf")
    elif platform.system() == "Windows" and os.path.exists(
        os.path.join(os.environ["APPDATA"], "pcreporter.conf")
    ):
        conf_to_read = os.path.join(os.environ["APPDATA"], "pcreporter.conf")

    if conf_to_read == None and os.path.exists("pcreporter.conf"):
        conf_to_read = "pcreporter.conf"
    else:
        raise FileNotFoundError("Configuration file not found.")

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

            if line[0] == "CHAT_ID":
                CHAT_ID = int(line[1])
            if line[0] == "IS_DEFENSIVE":
                IS_DEFENSIVE = bool(line[1])

            line_num += 1
