import sys


def info_temp():
    t_str = ""
    if sys.platform == "win32":
        return "Woomp Woomp, Not supported on Windows"
    else:
        import psutil

        res = psutil.sensors_temperatures()
        for key in res.keys():
            for sensor in res[key]:
                if sensor.label == "":
                    continue
                t_str += f"{sensor.label}: {sensor.current} °C"
                t_str += "\n"

    return f"""
<b>Temperature Information</b>
{t_str}
    """
