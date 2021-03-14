import psutil
import logging
import subprocess
import argparse
 
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
        subprocess.call(f"echo {message} | write {username} {terminal}")
 
def send_message_all_online(message):
    subprocess.call("wall %s" % message)
 
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--usr", default='online', type=str, help="Enter username or online or all")
    parser.add_argument("--message", default='Hi!', type=str, help="Your message")
    args = parser.parse_args()
    if args.usr == "online":
        send_message_all_online(args.message)
    else:
        send_message_to_user(args.usr, args.message)
 
main()
