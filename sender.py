#!/usr/bin/python3

import psutil
import logging
import subprocess
import argparse
import json
import datetime
import time
from db_connect import MessageboxDBConnector

FILTER_CONSTANT = 2500000

def get_user(username):
    founded = False
    terminal_list = []
    for user in psutil.users():
        if user.name == username:
            founded = True
            terminal_list.append(user.terminal)
    return((founded, terminal_list))


def send_message_to_user(username, message):
    usr = get_user(username)
    if usr[0] is False:
        logging.error('User %s is not online now' % username)
        return
    for terminal in usr[1]:
        #print(f"echo {message} | write {username} {terminal}")
        subprocess.call(f"echo {message} | write {username} {terminal}", shell=True)


def send_to_offline(username, message):
    db = MessageboxDBConnector()
    db.insert(user=username, message=message, ts=int(time.time()))

    '''msg = dict()
    messages = []
    with open('messagebox', 'r') as f:
        messages = json.load(f)

    for usr in usernames:
        if get_user(usr)[0] is False:
            msg['Text'] = message
            msg['Usr'] = usr
            curr_ts = int(datetime.datetime.now().timestamp())
            msg['Timestamp'] = curr_ts
            messages = list(filter(lambda x: curr_ts - x['Timestamp'] < FILTER_CONSTANT, messages))
            messages.append(msg)

    with open('messagebox', 'w') as f:
        json.dump(messages, f)'''


def get_user_list():
    PIPE = subprocess.PIPE
    p = subprocess.Popen("getent passwd | grep '/home'", shell=True, stdin=PIPE, stdout=PIPE,
        stderr=subprocess.STDOUT, close_fds=True)
    out = p.stdout.read()
    users = out.decode().split('\n')
    for i in range(len(users)):
        users[i] = users[i].split(':')[0]
    return users


def send_message_all_online(message):
    users = get_user_list()

    for usr in users:
        send_message_to_user(usr, message)

def send_message_all(message):
    users = get_user_list()
    # send_message_all_online(users, message)

    send_to_offline('all', message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--usr", default='zaikova', type=str, help="Enter username or online or all")
    parser.add_argument("--message", default='Hi!', type=str, help="Your message")

    args = parser.parse_args()
    if args.usr == "online":
        send_message_all_online(args.message)
    elif args.usr == "all":
        send_message_all(args.message)
    else:
        send_message_to_user(args.usr, args.message)
