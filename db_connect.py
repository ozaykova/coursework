
import psycopg2


class ChangeLogDBConnector:
    def __init__(self):
        self.conn = psycopg2.connect(dbname='changelog', user='daemon', password='daemon', host='localhost')
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def wrap_special(self, item):
        return item.replace('.', '\.')

    def insert(self, libname='', version='', upd_version='NULL', action='', ts=0):
        version = "\'" + version + "\'"
        libname = "\'" + libname + "\'"
        action = "\'" + action + "\'"
        self.cursor.execute(f"INSERT INTO libchangelog (LibName, Version, UpdVersion, Action, TS) VALUES ({libname}, {version}, {upd_version}, {action}, {ts});")
        self.conn.commit()

    def select_all(self):
        self.cursor.execute("SELECT * FROM libchangelog;")
        return self.cursor.fetchall()
