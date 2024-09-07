import sys


def fn_lock_screen():
    if sys.platform == "win32":
        import ctypes

        ctypes.windll.user32.LockWorkStation()
    else:
        import pcreporter.state as state

        if state.CMD_LOCKSCRN:
            import os

            os.system(state.CMD_LOCKSCRN)
        else:
            return """
            No lock screen command found in configuration.
            """

    return f"""
    Locked screen.
    """
