import psutil

def info_programs():
    app_list = []
    for proc in psutil.process_iter():
        try:
            app_list.append(proc.name())
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    app_list = list(set(app_list))

    app_str = ""
    index = 0
    for app in app_list:
        app_str += f"{app}"
        if index >= 3:
            app_str += "\n"
            index = 0
        else:
            app_str += ", "
            index += 1
    
    return f"""<b>Programs:</b>
{app_str}
    """
