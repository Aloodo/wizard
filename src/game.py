#!/usr/bin/env python3

from datetime import timezone
import logging
import os
import signal
import subprocess
import sys
import time

try:
    import psycopg2
except:
    print("This needs to be run on the server or container with Python dependencies installed.")
    sys.exit(0)

import config
from wizard import Wizard

class Game(object):
    FIXED = True
    UNFIXED = False

    def __init__(self, applog=None, start_demo_db=False):
        global logging
        if applog is not None:
            logging = applog
        self.logging = logging
        self.wizard = Wizard
        self.wizard.game = self
        if start_demo_db:
            self.start_demo_db()
        self.connect()

    def connect(self):
        for i in range(5):
            try: 
                self.conn = psycopg2.connect(database=config.DB_NAME, user=config.DB_USER, host=config.DB_HOST, port=config.DB_PORT)
                if i > 0:
                    logging.info("Connected to database after %d attempt(s)." % i)
                break
            except psycopg2.OperationalError:
                logging.info("Waiting for database.")
                time.sleep(2**(i+3))
        else:
            logging.error("Database connection failed")
            raise RuntimeError

    def start_demo_db(self):
        try:
            psycopg2.connect(database=config.DB_NAME, user=config.DB_USER, host=config.DB_HOST, port=config.DB_PORT)
            return
        except psycopg2.OperationalError:
            pass
        demo_db = subprocess.Popen(["/usr/bin/sudo", "-u", "postgres", "/usr/lib/postgresql/9.6/bin/postgres",
                                    "-D", "/var/lib/postgresql/9.6/main",
                                    "-c", "config_file=/etc/postgresql/9.6/main/postgresql.conf"],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logging.info("Started test database. PID is %d" % demo_db.pid)

    def stop_demo_db(self):
        self.conn.close()
        try:
            with open("/var/lib/postgresql/9.6/main/postmaster.pid") as pidfile:
                pidline = pidfile.readline()
            os.kill(int(pidline), signal.SIGKILL)
            logging.info("Waiting for test database to shut down.")
            time.sleep(1)
        except ProcessLookupError:
            pass

        while True:
            try:
                psycopg2.connect(database=config.DB_NAME, user=config.DB_USER, host=config.DB_HOST, port=config.DB_PORT)
            except:
                return

    def now(self):
        with self.conn.cursor() as curs:
            curs.execute("SELECT NOW()")
            when = curs.fetchone()[0]
            when = when.replace(tzinfo=timezone.utc)
            return when

# vim: autoindent textwidth=100 tabstop=4 shiftwidth=4 expandtab softtabstop=4 filetype=python
