# -*- coding: utf-8 -*-

import MySQLdb
import ConfigParser

class PearMySQL:
    def __init__(self, conf_path):
        """ initialize """
        self.conf = self.getConfig(conf_path)
        self.connector = None
        self.cursor = None

    def getConfig(self, conf_path):
        """ set configure """
        conf = ConfigParser.SafeConfigParser()
        conf.read(conf_path)
        return conf

    def openDB(self):
        """ open database """
        self.openConnect()
        self.openCursor()

    def closeDB(self):
        """ close database """
        self.closeCursor()
        self.closeConnector()

    def openConnect(self):
        """ set connector for database """
        self.connector = MySQLdb.connect(
            host=self.conf.get("mysql", "host"),
            db=self.conf.get("mysql", "db"),
            user=self.conf.get("mysql", "user"),
            passwd=self.conf.get("mysql", "passwd")
        )

    def openCursor(self):
        """ set cursor for database """
        self.cursor = self.connector.cursor(MySQLdb.cursors.DictCursor)

    def closeConnector(self):
        """ close connector for database """
        self.connector.close()

    def closeCursor(self):
        """ close cursor for database """
        self.cursor.close()

    def queryFetch(self, query):
        self.openDB()
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        self.closeDB()
        return results

    def query(self, query):
        self.openDB()
        self.cursor.execute(query)
        self.connector.commit()
        self.closeDB()
