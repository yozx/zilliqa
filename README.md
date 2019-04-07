# zilliqa
things for zilliqa

**zil_switch.py**
```
READ BEFORE START:
[1] You need python 3.6+ & urllib3 installed on your machine
    You can download python here: https://www.python.org/downloads/
    You can install urllib3 by type 'py -m pip install urllib3' in console/Command Promt
[TIPS]: Ignore pip upgrading message, it will broke things up
        Setting up virtualenv is a good practice. Docs: https://virtualenv.pypa.io/en/stable/userguide/
        but it's not necessary
[2] You need to create folder structure as noted below!
[3] For starting script navigate to [Root folder] and
    type 'python3 zil_switch.py' or 'py zil_switch.py' at Command Prompt
[4] There some bugs, so don't expected smooth running all time long
[5] When script is running, shutdown it properly using [CTRL + C] in Command Prompt
Folder structure:
.                              # Root folder
├── other                      # Put miner files and run.bat file in this folder
├── zilliqa                    # Put zilliqa miner files and run.bat file in this folder
├── zil_switch.py              # Source script

HOW SCRIPT WORKS:
    Script checking https://api.zilliqa.com/ endpoint every 30 sec by default for current block number.
    When network reaches block in range ..98 - ..99, script shutdown all miner tasks and start zilliqa miner -> [Zilliqa state]
    When network reaches block in range ..01 - ..02 it does opposite thing -> [Other miner state]
        If script runs [Zilliqa state] > TIMEOUT (15 min default) it will switch back to [Other miner state]

NOTES:
    If network stuck's at range ..98 - ..99 script starts running infinity loop ¯\_(ツ)_/¯
    There are no logs, but you can check main Command Prompt/console for some info
```
