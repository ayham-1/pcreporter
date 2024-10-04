import os
import logging
import subprocess
import json

logger = logging.getLogger("pcreporter")


def fn_tailscale_up():
    # you have to first run sudo tailscale up --operator=$USER 
    # before being able to use non sudo tailscale commands
    try:
        subprocess.check_output(["tailscale", "up"])
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.decode('utf-8')}"

    return "Tailscale is up"

def fn_tailscale_down():
    try:
        subprocess.check_output(["tailscale", "down"])
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.decode('utf-8')}"

    return "Tailscale is down"


def fn_tailscale_status():
    results = subprocess.check_output(["tailscale", "status", "--json"]).decode("utf-8")
    data = json.loads(results)
    msg = ""

    msg += f"""
<b>Current Tailnet:</b>
Name: {data["CurrentTailnet"]["Name"]}
Magic DNS Suffix: {data["CurrentTailnet"]["MagicDNSSuffix"]}
Magic DNS Enabled: {data["CurrentTailnet"]["MagicDNSEnabled"]}

<b>Current System:</b>
Online: {data["Self"]["Online"]}
DNS Name: {data["Self"]["DNSName"]}

Tailscale IPs: {','.join(data["Self"]["TailscaleIPs"])}
Addresses: {','.join(data["Self"]["Addrs"])}

<b>Peers:</b>
"""

    for peer in data["Peer"]:
        msg += f"""
<b>{data["Peer"][peer]["HostName"]}</b>
Online: {data["Peer"][peer]["Online"]}
DNS Name: {data["Peer"][peer]["DNSName"]}
Tailscale IP: {','.join(data["Peer"][peer]["TailscaleIPs"])}
OS: {data["Peer"][peer]["OS"]}
"""
    return msg
