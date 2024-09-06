import psutil


def info_temp():
    res = psutil.sensors_temperatures()
    t_str = ""
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
