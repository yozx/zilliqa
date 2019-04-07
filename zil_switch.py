"""
Made by Yan. 2019

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
"""

import urllib3
import json
from time import sleep, ctime, time
import os
import subprocess
import csv

http = urllib3.PoolManager()
urllib3.disable_warnings()  # Disable SSL cert warning
cwd = os.path.dirname(os.path.abspath(__file__)) + '/'
ZIL_FILENAME = 'run.bat'
OTHER_FILENAME = 'run.bat'  # TODO Replace with sys.args
PATH_ZILLIQA = cwd + '/zilliqa/'
PATH_OTHER = cwd + '/other/'
TIMEOUT = 15 * 2  # Time to switch back from Zilliqa. Default 15 min.
START = time()
SLEEP = 60 / 2  # Idle time between block checking in sec. Default 30 sec.


def get_data():
    """
    Fetching data from https://api.zilliqa.com/
    DOCS: https://apidocs.zilliqa.com/#introduction
    :return: Current block num
    """
    data = {"id": 1,
            "jsonrpc": "2.0",
            "method": "GetBlockchainInfo",
            "params": [""]
            }
    encoded_data = json.dumps(data).encode('utf-8')
    try:
        r = http.request('POST', 'https://api.zilliqa.com/',
                         body=encoded_data,
                         headers={'Content-Type': 'application/json'},
                         retries=10)

        response = json.loads(r.data.decode('utf-8'))
        return response['result']['CurrentMiniEpoch']
    except urllib3.exceptions.NewConnectionError as err:
        print('Got network error', err)
        raise SystemExit


def get_current_user_processes():
    """
    Converts useless tasklist format to plain rows
    :return: dict of currently fetched processes
    """
    csv_output = subprocess.check_output(["tasklist", "/FI", "USERNAME eq {}".format(os.getenv("USERNAME")),
                                          "/FO", "CSV"]).decode("ascii", "ignore")
    cr = csv.reader(csv_output.splitlines())
    next(cr)   # skip title lines
    return {int(row[1]): row[0] for row in cr}


def kill(tasks):
    """
    Killing all processes and child process too
    """
    for name, pid in tasks.items():
        print(name, pid)
        try:
            if name != 'tasklist.exe':
                subprocess.run("Taskkill /PID %d /t /f" % pid)
                sleep(1)
        except KeyError as e:
            print('Got', e)  # pass this error
    print('All process killed', ctime())


def start_and_get_id(filename, path):
    prev_tasks = get_current_user_processes()
    os.chdir(path)
    os.system('START ' + filename)
    print('Start', filename, ctime())
    sleep(15)  # Give some time to get all new tasks
    print('Gathering new tasks..')
    new_tasks = get_current_user_processes()
    curr_tasks = {new_tasks[pid]: pid for pid in set(new_tasks) - set(prev_tasks)}
    print('Current tasks:', curr_tasks)
    return curr_tasks


def run_once():
        get_data()  # Checking network connection
        print('Start', ctime(), 'Press [CTRL + C] for exit')
        tasks = start_and_get_id(OTHER_FILENAME, PATH_OTHER)
        return tasks


def main(tasks):
    """
    This contains all logic of switch
    """
    case, timer, timer_running = False, 0, False
    try:
        while True:
            block_num = get_data()
            print('Current block:', block_num, ctime())

            if case is False and block_num[-2:] in ['98', '99']:
                kill(tasks)
                tasks = start_and_get_id(ZIL_FILENAME, PATH_ZILLIQA)
                case = True
                timer_running = True
            elif case is True and block_num[-2:] in ['01', '02'] or case is True and timer >= TIMEOUT:
                kill(tasks)
                tasks = start_and_get_id(OTHER_FILENAME, PATH_OTHER)
                case = False
                timer, timer_running = 0, False
            else:
                pass

            sleep(SLEEP)
            if timer_running is True:
                timer += 1
    # Some sort of gracefully shutdown
    except KeyboardInterrupt:
            print('Shutting down..\nWorked time:', time() - START, 's')
            kill(tasks)
            raise SystemExit


if __name__ == '__main__':
    first_tasks = run_once()

    # Main loop started
    main(first_tasks)
