import os


class State:
    __CHAT_ID__ = None
    __IS_DEFENSIVE__ = False

    def __init__(self):
        self.__CHAT_ID__ = None
        self.__IS_DEFENSIVE__ = False

    def read_config(self):
        """Read configuration file into self."""
        conf_to_read = None

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
        else:
            if not os.path.exists("pcreporter.conf"):
                raise FileNotFoundError("Configuration file not found.")
            conf_to_read = "pcreporter.conf"

        with open(conf_to_read, "r") as f:
            for line in f.readlines():
                if line.startswith("CHAT_ID="):
                    self.__CHAT_ID__ = int(line.split("=")[1])
                if line.startswith("IS_DEFENSIVE="):
                    self.__IS_DEFENSIVE__ = bool(line.split("=")[1])
