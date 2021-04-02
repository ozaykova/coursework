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
        for i in range(0, len(lines), 4):
            if int(lines[i + 3]) > ts:
                print("Library " + str(lines[i + 1]) + " " + lines[i] + " version " + lines[i + 2])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--usr", default='zaikova', type=str, help="Enter username for report generating")
    parser.add_argument("--date", default='2020-01-01', type=str, help="Start date")

    args = parser.parse_args()

    date = parse(args.date).timestamp()

    parse_messages(args.usr, date)
    parse_libs(args.usr, date)

main()
