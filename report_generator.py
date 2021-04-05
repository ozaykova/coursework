import argparse
import datetime as dt
import json
from dateutil.parser import parse

def parse_messages(user, ts):
    print('Your messages:')
    with open('messagebox', 'r') as f:
        messages = json.load(f)
        messages = list(filter(lambda x: x['Timestamp'] >= ts and x['Usr'] == user, messages))
        for msg in messages:
            print(msg['Text'])


def parse_libs(user, ts):
    with open('../lib_change_log', 'r') as f:
        lines = f.readlines()

        updates = dict()
        i = 0
        while i < len(lines):
            if lines[i] == "add" or lines[i] == "del":
                print("Library " + str(lines[i + 1]) + " " + lines[i] + " version " + lines[i + 2])
                i += 3
            elif lines[i] == "upd":
                if lines[i + 1] in updates:
                    updates[lines[i + 1]]['to'] = lines[i + 3]
                else:
                    upd = dict()
                    upd['from'] = lines[i + 2]
                    upd['to'] = lines[i + 3]
                    updates[lines[i + 1]] = upd
                i += 4


        for lib in updates:
            print("Library " + str(lines[i + 1]) + " was updated from " + lib['from'] + " to " + lib['to'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--usr", default='zaikova', type=str, help="Enter username for report generating")
    parser.add_argument("--date", default='2020-01-01', type=str, help="Start date")

    args = parser.parse_args()

    date = parse(args.date).timestamp()

    parse_messages(args.usr, date)
    parse_libs(args.usr, date)

main()
