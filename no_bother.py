#!/usr/bin/python3

import os
import pwd
import time
import subprocess
from report_generator import ReportGenerator
from sender import send_message_all_online, send_message_all, send_message_to_user

MONTH = 2500000
WEEK = 600000

class InstalHelpers:
    def owner(self, pid):
        for ln in open('/proc/%d/status' % pid):
            if ln.startswith('Uid:'):
                uid = int(ln.split()[1])
                return pwd.getpwuid(uid).pw_name

    def get_ts_month_ago(self):
        return int(time.time()) - MONTH

    def get_ts_week_ago(self):
        return int(time.time()) - WEEK


def main():
    print('Select an action: \n [1] Generate user report(default) \n [2] Generate library report \n [3] Send message \n [4] Use apt-get')
    action_type = input()
    rg = ReportGenerator()
    helper = InstalHelpers()
    if action_type == '1':
        pid = os.getpid()
        print('Select time period: \n [1] Week (default) \n [2] Month')
        time_period = input()
        if time_period == '2':
            rg.perform(helper.owner(pid), helper.get_ts_month_ago())
        else:
            rg.perform(helper.owner(pid), helper.get_ts_week_ago())
    elif action_type == '2':
        print('Select time period: \n [1] Week (default) \n [2] Month')
        time_period = input()
        print('Enter lib name:')
        lib = input()
        if time_period == '2':
            rg.get_db_lib_changes(helper.get_ts_month_ago(), lib)
        else:
            rg.get_db_lib_changes(helper.get_ts_week_ago(), lib)
    elif action_type == '3':
        print('Select addressee: \n [1] All online \n [2] All users \n [3] Concrete user(default)')
        addressee = input()
        if addressee == '1':
            print('Enter your message')
            msg = input()
            send_message_all_online(msg)
        elif addressee == '2':
            print('Enter your message')
            msg = input()
            send_message_all(msg)
        else:
            print('Enter user name')
            usr = input()
            print('Enter your message')
            msg = input()
            send_message_to_user(usr, msg)
    else:
        print('Select action: \n [1] Install(default) \n [2] Delete \n [3] Update')
        action = input()
        if action == '2':
            print('Enter lib name:')
            lib = input()
            subprocess.Popen(f"curl http://127.0.0.1:8000/delete?lib={lib}", shell=True)
        elif action == '3':
            subprocess.Popen(f"curl http://127.0.0.1:8000/update", shell=True)
        else:
            print('Enter lib name:')
            lib = input()
            subprocess.Popen(f"curl http://127.0.0.1:8000/add?lib={lib}", shell=True)



main()
