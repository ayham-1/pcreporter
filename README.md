# pcreporter

Telegram BOT as a personal computer reporting service. 


## Features:

- system overview reporting
- temperature reporting
- USB reporting and monitoring
- defensive and observative modes 
- remote shutdown and screen lock
- single chat user allowed to interact with the bot

## Setup:

1. Install the package from PyPi.
```
pipx install pcreporter
```

2. Create a bot on Telegram and get the token.
3. Create config file in the following format:
```
CHAT_ID=<chat_id>
IS_DEFENSIVE=false
CMD_LOCKSCRN=swaylock -f -c 000000 <replace with custom command if needed>
TOKEN=<telegram bot token>
```
To get the CHAT_ID value, run the bot with CHAT_ID of 0 and send a message to it. The CHAT_ID will be reported in the terminal and messaged back to the user on Telegram.

The config file could be placed in the following locations:
- /etc/pcreporter.conf
- ~/.config/pcreporter.conf
- ~/.pcreporter.conf
- (current working directory)/pcreporter.conf

4. Run the bot.
> **Warning**
> Do not run the bot as root. The bot will refuse to run if run as root (intentional design).
> For poweroff functionality, ensure you can run the command 'poweroff' as the non-root user.

5. (Optional) Tailscale Support: in order to be able to turn the network on and off without root privileges:

```
sudo tailscale down
sudo tailscale up --operator=$(whoami)
```

### Setup Tip: Using SystemD User Services
To run the bot as a user service, copy the file `pcreporter.service` form this repository to `~/.config/systemd/user/pcreporter.service` and enable it with `systemctl --user enable --now pcreporter.service`.


## Maintainers:
- [ayham-1](https://me@ayham.xyz)

## Used Python Packages:
- python-telegram-bot
- psutil
- requests
- uptime
- usb-monitor
