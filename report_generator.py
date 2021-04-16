import argparse
import datetime as dt
import json
from dateutil.parser import parse
from db_connect import ChangeLogDBConnector, MessageboxDBConnector


class ReportGenerator:
    def parse_messages(self, user, ts):
        print('Your messages:')
        db = MessageboxDBConnector()
        t = str(ts)
        rows = db.select_where(statement=f'TS > {t} AND (username = \'{user}\' OR username = \'all\')')
        for row in rows:
            print(row[0])


    def parse_libs(self, user, ts):
        with open('../lib_change_log', 'r') as f:
            lines = f.readlines()

            updates = dict()
            i = 0
            while i < len(lines):
                print(lines[i])
                if "add" in lines[i] or "del" in lines[i]:
                    print("Library " + str(lines[i + 1]) + " " + lines[i] + " version " + lines[i + 2])
                    i += 4
                elif "upd" in lines[i]:
                    if lines[i + 1] in updates:
                        updates[lines[i + 1]]['to'] = lines[i + 3]
                    else:
                        upd = dict()
                        upd['from'] = lines[i + 2]
                        upd['to'] = lines[i + 3]
                        updates[lines[i + 1]] = upd
                    i += 5


            for lib in updates:
                print("Library " + str(lines[i + 1]) + " was updated from " + lib['from'] + " to " + lib['to'])

    def print_report(self, rows, ts):
        for row in rows:
            if row[4] > ts:
                if row[3] == 'add':
                    print(row[0] + " was added with version " + row[1])
                elif row[3] == 'del':
                    print(row[0] + " was deleted with version " + row[1])
                elif row[3] == 'upd':
                    print(row[0] + " was updated from " + row[1] + " to " + row[2])


    def get_db_lib_changes(self, ts, lib='all'):
        print('Packages changes:')
        db = ChangeLogDBConnector()

        rows = None
        if lib != 'all':
            rows = db.select_where(f'libname = \'{lib}\'')
        else:
            rows = db.select_all()
        self.print_report(rows, ts)


    def perform(self, usr, ts):
        self.parse_messages(usr, ts)
        self.parse_libs(usr, ts)
        self.get_db_lib_changes(ts)



'''def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--usr", default='zaikova', type=str, help="Enter username for report generating")
    parser.add_argument("--date", default='2020-01-01', type=str, help="Start date")

    args = parser.parse_args()

    date = parse(args.date).timestamp()

    generator = ReportGenerator()

    generator.perform(args.usr, date)


main()'''
