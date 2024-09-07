import os
import logging

logger = logging.getLogger("pcreporter")


def fn_shutdown():
    logger.info("Shutting down the system...")
    os.system("shutdown -s")
    return "Shutting down the system..."
