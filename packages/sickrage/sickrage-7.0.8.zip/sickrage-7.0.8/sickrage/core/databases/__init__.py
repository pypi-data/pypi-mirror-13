# -*- coding: utf-8 -*
# Author: echel0n <sickrage.tv@gmail.com>
# URL: https://sickrage.tv
# Git: https://github.com/SiCKRAGETV/SickRage.git
#
# This file is part of SickRage.
#
# SickRage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SickRage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickRage.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

try:
    import queue as Queue  # module re-named in Python 3
except ImportError:
    import Queue

import time
import uuid
import os
import re
import sqlite3
import threading
import sickrage

from core.helpers import backupVersionedFile, restoreVersionedFile

__all__ = ["main_db", "cache_db", "failed_db"]


def prettyName(class_name):
    return ' '.join([x.group() for x in re.finditer("([A-Z])([a-z0-9]+)", class_name)])


def dbFilename(filename=None, suffix=None):
    """
    @param filename: The sqlite database filename to use. If not specified,
                     will be made to be sickrage.db
    @param suffix: The suffix to append to the filename. A '.' will be added
                   automatically, i.e. suffix='v0' will make dbfile.db.v0
    @return: the correct location of the database file.
    """

    filename = filename or 'sickrage.db'

    if suffix:
        filename = filename + ".{}".format(suffix)
    return os.path.join(sickrage.DATA_DIR, filename)


class Connection(threading.Thread):
    def __init__(self, filename=None, suffix=None, row_type=None, timeout=20, max_queue_size=100):
        threading.Thread.__init__(self)
        self.daemon = True

        self.filename = dbFilename(filename, suffix)
        self.row_type = row_type or sqlite3.Row

        self.conn = sqlite3.connect(self.filename,
                                    check_same_thread=False,
                                    timeout=timeout,
                                    detect_types=sqlite3.PARSE_DECLTYPES)

        self.conn.row_factory = (self._dict_factory, self.row_type)[self.row_type != 'dict']
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.cursor = self.conn.cursor()

        self.sql_queue = Queue.Queue(maxsize=max_queue_size)
        self.results = {}
        self.max_queue_size = max_queue_size
        self.exit_set = False

        # Token that is put into queue when close() is called.
        self.exit_token = str(uuid.uuid4())
        self.start()
        self.thread_running = True

    def run(self):
        execute_count = 0
        for token, query, values in iter(self.sql_queue.get, None):
            sickrage.srLogger.db("sql_queue: %s", self.sql_queue.qsize())
            if token != self.exit_token:
                sickrage.srLogger.db("run: %s", query)
                self.run_query(token, query, values)
                execute_count += 1

                if self.sql_queue.empty() or execute_count == self.max_queue_size:
                    self.conn.commit()
                    execute_count = 0

            if self.exit_set and self.sql_queue.empty():
                self.conn.commit()
                self.conn.close()
                self.thread_running = False
                return

    def run_query(self, token, query, values):
        attempt = 0
        while attempt <= 5:
            attempt += 1

            try:
                if query.lower().strip().startswith("select") or query.lower().strip().startswith("pragma"):
                    try:
                        self.cursor.execute(query, values)
                        self.results[token] = self.cursor.fetchall()
                        raise StopIteration
                    except sqlite3.Error as err:
                        sickrage.srLogger.error("Query returned error: %s: %s: %s", query, values, err)
                        self.results[token] = []
                else:
                    try:
                        self.cursor.execute(query, values)
                    except sqlite3.Error as err:
                        sickrage.srLogger.error("Query returned error: %s: %s: %s", query, values, err)
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                self.conn.rollback()
                time.sleep(1)
            except StopIteration:
                break

    def close(self):
        self.exit_set = True
        self.sql_queue.put((self.exit_token, "", ""), timeout=5)
        while self.thread_running:
            time.sleep(.01)  # Don't kill the CPU waiting.

    @property
    def queue_size(self):
        return self.sql_queue.qsize()

    def query_results(self, token):
        delay = .001
        while True:
            if token in self.results:
                return_val = self.results[token]
                del self.results[token]
                return return_val

            time.sleep(delay)
            if delay < 8:
                delay += delay

    def _execute(self, query, values=None):
        if self.exit_set:
            return "Exit Called"

        sickrage.srLogger.db("execute: %s", query)
        values = values or []

        # A token to track this query with.
        token = str(uuid.uuid4())

        # If it's a select we queue it up with a token to mark the results
        # into the output queue so we know what results are ours.
        if query.lower().strip().startswith("select") or query.lower().strip().startswith("pragma"):
            self.sql_queue.put((token, query, values), timeout=5)
            return self.query_results(token)

        self.sql_queue.put((token, query, values), timeout=5)

    def upsert(self, tableName, valueDict, keyDict):
        """
        Update values, or if no updates done, insert values

        :param tableName: table to update/insert
        :param valueDict: values in table to update/insert
        :param keyDict:  columns in table to update
        """

        # update existing row if exists
        genParams = lambda myDict: [x + " = ?" for x in myDict.keys()]
        query = "UPDATE [" + tableName + "] SET " + ", ".join(
            genParams(valueDict)) + " WHERE " + " AND ".join(genParams(keyDict))
        self._execute(query, *valueDict.values() + keyDict.values())

        if not self.conn.total_changes:
            # insert new row if update failed
            query = "INSERT INTO [" + tableName + "] (" + ", ".join(
                valueDict.keys() + keyDict.keys()) + ")" + " VALUES (" + ", ".join(
                ["?"] * len(valueDict.keys() + keyDict.keys())) + ")"
            self.cursor.execute(query, *valueDict.values() + keyDict.values())

        return (False, True)[self.conn.total_changes > 0]

    def getChanges(self):
        return self.action("SELECT changes();")

    def checkDBVersion(self):
        """
        Fetch database version

        :return: Integer inidicating current DB version
        """
        try:
            if self.hasTable('db_version'):
                return self.select("SELECT db_version FROM db_version")
        except:
            return 0

    def mass_upsert(self, upserts):
        """
        Execute multiple upserts

        :param upserts: list of upserts
        :return: list of results
        """

        sqlResults = [self.upsert(u[0], u[1], u[2]) for u in upserts]
        sickrage.srLogger.db("{} Upserts executed".format(len(upserts)))
        return sqlResults

    def mass_action(self, queries):
        """
        Execute multiple queries

        :param queries: list of queries
        :return: list of results
        """
        sqlResults = [self._execute(q) for q in queries]
        sickrage.srLogger.db("{} Transactions executed".format(len(queries)))
        return sqlResults

    def action(self, query, *args):
        """
        Execute single query

        :rtype: query results
        :param query: Query string
        """

        sickrage.srLogger.db("{}: {} with args {}".format(self.filename, query, args))
        return self._execute(query, *args)

    def select(self, query, *args):
        """
        Perform single select query on database

        :param query: query string
        :param args:  arguments to query string
        :rtype: query results
        """
        return self._execute(query, *args)

    def tableInfo(self, tableName):
        """
        Return information on a database table

        :param tableName: name of table
        :return: array of name/type info
        """
        columns = {}

        sqlResult = self.select("PRAGMA table_info(`{}`)".format(tableName))

        for column in sqlResult:
            columns[column[b'name']] = {'type': column[b'type']}

        return columns

    def _dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def hasIndex(self, indexName):
        """
        Check if a index exists in database

        :param indexName: index name to check
        :return: True if table exists, False if it does not
        """
        return (False, True)[len(self.select("PRAGMA index_info('{}')".format(indexName))) > 0]

    def hasTable(self, tableName):
        """
        Check if a table exists in database

        :param tableName: table name to check
        :return: True if table exists, False if it does not
        """
        return (False, True)[len(self.select("SELECT 1 FROM sqlite_master WHERE name = ?", [tableName])) > 0]

    def hasColumn(self, tableName, column):
        """
        Check if a table has a column

        :param tableName: Table to check
        :param column: Column to check for
        :return: True if column exists, False if it does not
        """
        return column in self.tableInfo(tableName)

    def addColumn(self, table, column, type="NUMERIC", default=0):
        """
        Adds a column to a table, default column type is NUMERIC
        TODO: Make this return true/false on success/failure

        :param table: Table to add column too
        :param column: Column name to add
        :param type: Column type to add
        :param default: Default value for column
        """
        self.action("ALTER TABLE [%s] ADD %s %s" % (table, column, type))
        self.action("UPDATE [%s] SET %s = ?" % (table, column), default)

    def incDBVersion(self):
        self.action("UPDATE db_version SET db_version = db_version + 1")


class SchemaUpgrade(Connection):
    def __init__(self, filename=None, suffix=None, row_type=None):
        super(SchemaUpgrade, self).__init__(filename, suffix, row_type)

    def upgrade(self):
        """
        Perform database upgrade and provide logging
        """

        def _processUpgrade(upgradeClass, version):
            name = prettyName(upgradeClass.__name__)

            while (True):
                sickrage.srLogger.debug("Checking {} database structure".format(name))

                try:
                    instance = upgradeClass()

                    if not instance.test():
                        sickrage.srLogger.debug("Database upgrade required: {}".format(name))
                        instance.execute()
                        sickrage.srLogger.debug("{} upgrade completed".format(name))
                    else:
                        sickrage.srLogger.debug("{} upgrade not required".format(name))

                    return True
                except sqlite3.DatabaseError:
                    if not self.restore(version):
                        break

        for klass in self.get_subclasses():
            _processUpgrade(klass, self.checkDBVersion())

    def restore(self, version):
        """
        Restores a database to a previous version (backup file of version must still exist)

        :param version: Version to restore to
        :return: True if restore succeeds, False if it fails
        """

        sickrage.srLogger.info("Restoring database before trying upgrade again")
        if not restoreVersionedFile(dbFilename(suffix='v' + str(version)), version):
            sickrage.srLogger.info("Database restore failed, abort upgrading database")
            return False
        return True

    def backup(self, version):
        sickrage.srLogger.info("Backing up database before upgrade")
        if not backupVersionedFile(dbFilename(), version):
            sickrage.srLogger.log_error_and_exit("Database backup failed, abort upgrading database")
        else:
            sickrage.srLogger.info("Proceeding with upgrade")

    @classmethod
    def get_subclasses(cls):
        yield cls
        if cls.__subclasses__():
            for sub in cls.__subclasses__():
                for s in sub.get_subclasses():
                    yield s
