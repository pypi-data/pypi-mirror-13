__author__ = 'dcortes'

import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.errorcodes import lookup


class PostgresConnector():

    def __init__(self, settings):
        self._settings = settings

    def _connect_postgres(self):
        conn = psycopg2.connect(database=self._settings["db"],
                                user=self._settings["user"],
                                password=self._settings["password"],
                                host=self._settings["host"],
                                port=self._settings["port"],
                                cursor_factory=DictCursor)
        return conn.cursor(), conn

    def _disconnect_postgres(self, cur, conn):
        cur.close()
        conn.close()

    def get(self, query, vars):
        try:
            cur, conn = self._connect_postgres()
            cur.execute(query, vars=vars)
            result = cur.fetchone()
            self._disconnect_postgres(cur, conn)
            return result
        except Exception, e:
            error = lookup(e.pgcode)
            raise Exception("dexma_drivers - postgres - error executing execute query {}".format(error))

    def fetch(self, query, vars):
        try:
            cur, conn = self._connect_postgres()
            cur.execute(query, vars=vars)
            result = cur.fetchall()
            self._disconnect_postgres(cur, conn)
            return result
        except Exception, e:
            error = lookup(e.pgcode)
            raise Exception("dexma_drivers - postgres - error executing execute query {}".format(error))

    def insert(self, query, vars):
        try:
            cur, conn = self._connect_postgres()
            cur.execute(query, vars=vars)
            conn.commit()
            self._disconnect_postgres(cur, conn)
            return True
        except Exception, e:
            error = lookup(e.pgcode)
            raise Exception("dexma_drivers - postgres - {} in postgres sql".format(error.capitalize()))
