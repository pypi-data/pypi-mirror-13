#-*- encoding: utf-8 -*-

__author__ = "Damian Kęska"
__license__ = "LGPLv3"
__maintainer__ = "Damian Kęska"
__copyright__ = "Copyleft by Panthera Desktop Team"

import sys
import codecs
import traceback

try:
    import MySQLdb
    import MySQLdb.cursors
except ImportError:
    pass
    
try:
    import sqlite3
except ImportError:
    pass
    
try:
    from peewee import *
    import peewee
except ImportError:
    pass

try:
    from pymongo import MongoClient
except ImportError:
    pass

class pantheraDB:
    """
        Database support
    """
    
    panthera = None
    db = None
    cursor = None
    dbType = None
    escapeFunc = None

    def __init__(self, panthera):
        """ Initialize connection """
    
        self.panthera = panthera
        
        self.panthera.logging.output("Initializing pantheraDB", "pantheraDB")
        
        # Create some default configuration keys
        self.panthera.config.getKey('databaseHost', 'localhost')
        self.panthera.config.getKey('databasePassword', '')
        self.panthera.config.getKey('databaseUser', 'root')
        self.panthera.config.getKey('databaseDB', 'my-database')
        self.panthera.config.getKey('databaseFile', self.panthera.filesDir+"/db.sqlite3")
        
        
        if not "MySQLdb" in globals() and not "sqlite3" in globals() and not "peewee" in globals():
            self.panthera.logging.output("No MySQL or SQLite3 driver found", "pantheraDB")
            sys.exit(1)
            
        try:
            dbType = self.panthera.config.getKey('databaseType', 'orm').lower()
            
            ###
             #
             # Peewee ORM database
             #
            ###
            
            if dbType == 'orm':
                if not "peewee" in globals():
                    self.panthera.logging.output("Peewee module not found, but orm database type selected", "pantheraDB")
                    sys.exit(1)
                
                if self.panthera.config.getKey("databaseSocketType", "sqlite3") == "sqlite3":
                    self.db = db = SqliteDatabase(self.panthera.config.getKey('databaseFile', self.panthera.filesDir+"/db.sqlite3"))
                    
                    class BaseModel(Model):
                        class Meta:
                            database = db
                    
                    self.BaseModel = BaseModel
                    self.dbType = "peewee"
                
            ###
             #
             # SQLite3 native support
             #
            ###
            
            elif dbType == 'sqlite3':
                self.db = sqlite3.connect(self.panthera.config.getKey('databaseFile'), check_same_thread=False)
                self.db.row_factory = dict_factory
                self.cursor = self.db.cursor()
                self.dbType = "sqlite3"
                self.escapeFunc = quoteIdentifier
                
            ###
             #
             # MySQL (MySQLdb driver)
             #
            ###
                
            elif dbType == 'mysql':
                
                self.db = MySQLdb.connect(
                    host=self.panthera.config.getKey('databaseHost'),
                    user=self.panthera.config.getKey('databaseUser'),
                    passwd=self.panthera.config.getKey('databasePassword'),
                    db=self.panthera.config.getKey('databaseDB'),
                    cursorclass=MySQLdb.cursors.DictCursor
                )
                
                # escape function
                self.escapeFunc = self.db.escape_string
                
                self.cursor = self.db.cursor()
                self.dbType = "mysql"
                
            ###
             #
             # MongoDB
             #
            ###
            
            elif dbType == 'mongodb':
                self.db = MongoClient(str(self.panthera.config.getKey('databaseHost')), int(self.panthera.config.getKey('databasePort', 27017)))
                
                if self.panthera.config.getKey('databaseUser') and self.panthera.config.getKey('databasePassword'):
                    self.db.the_database.authenticate(self.panthera.config.getKey('databaseUser'), self.panthera.config.getKey('databasePassword'))
                
                self.dbType = "mongodb"
            else:
                self.panthera.logging.output("Unknown database driver \'"+str(self.panthera.config.getKey('databaseType'))+"\'", "pantheraDB")
                sys.exit(1)
                
            self.panthera.logging.output("Connection estabilished using "+self.dbType+" socket", "pantheraDB")
        except Exception as e:
            self.panthera.logging.outputException("Cannot connect to database: "+str(e), "pantheraDB")
            sys.exit(1)


    def query(self, query, values=dict(), commit=True):
        """ Execute a raw query """
        
        ###
         # Append database prefix and insert values into a query
        ###

        # {$db_prefix} insertion support
        query = query.replace('{$db_prefix}', str(self.panthera.config.getKey('databasePrefix', 'pa_')))
        originalQuery = query

        # inserting escaped values into query
        query, values = self.applyValues(query, values)

        if query.strip() != originalQuery.strip():
            self.panthera.logging.output("Original: " + query, "pantheraDB")

        self.panthera.logging.output("SQL: "+ query, "pantheraDB")

        ###
         # Make q query and return a resultset
        ###
        
        if self.dbType == "peewee":
            return self.db.execute_sql(query, values)
            
        elif self.dbType == "sqlite3":
            obj = self.cursor.execute(query, values)
            
            if commit:
                self.db.commit()
                
            return pantheraDBSQLite3ResultSet(obj, self.cursor)
        
        elif self.dbType == 'mysql':
            obj = self.cursor.execute(query, values)
            
            if commit:
                self.db.commit()
                
            return pantheraDBMySQLResultSet(self.cursor, self, obj)
        
        elif self.dbType == 'mongodb':
            raise Exception('query() is not supported by MongoDB database type')
        else:
            self.panthera.logging.output("Cannot connect to databse via unknown socket", "pantheraDB")
            sys.exit(1)



    def applyValues(self, query, values):
        """ Append values from dict to query string """

        newValues = []

        for value in values:
            pos = query.find(':' + value)

            while pos != -1:
                query = query[:pos] + '?' + query[pos + len(':' + value):]
                newValues.append(values[value])

                pos = query.find(':' + value)

        return query, newValues



class pantheraDBSQLite3ResultSet:
    """ Result set for SQLite3 """

    db = None
    cursor = None
    lastrowid = None
    indexColumn = None

    def __init__(self, cursor, db, result=''):
        self.db = db
        self.cursor = cursor
        self.lastrowid = 0
        
        if cursor:
            self.lastrowid = cursor.lastrowid
        
    def indexColumn(self, columnName):
        """ Column to index by """
    
        self.indexColumn = columnName
        return self
        
    def rowCount(self):
        """ Count affected/selected rows """
        
        if not self.cursor:
            return 0
    
        rowCount = self.cursor.rowcount
        
        if rowCount < 0:
            rowCount = 0
        
        return rowCount
        
    def fetchAll(self):
        """ Fetch all rows """
        
        if not self.cursor:
            return list()
    
        f = self.cursor.fetchall()
        
        if self.indexColumn is not None and len(f) > 0 and f[0].has_key(self.indexColumn):
            newArray = dict()
        
            for row in f:
                newArray[row[self.indexColumn]] = row
                
            f = newArray
    
        return f
        
    def fetch(self):
        """ Fetch one row """
        
        if not self.cursor:
            return False
    
        return self.cursor.fetchone()

    
class pantheraDBMySQLResultSet(pantheraDBSQLite3ResultSet):
    """ Result set for SQLite3 """

    db = None
    cursor = None
    lastrowid = None
    indexColumn = None
    
def quoteIdentifier(s, errors="strict"):
    encodable = s.encode("utf-8", errors).decode("utf-8")

    nul_index = encodable.find("\x00")

    if nul_index >= 0:
        error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                                   nul_index, nul_index + 1, "NUL not allowed")
        error_handler = codecs.lookup_error(errors)
        replacement, _ = error_handler(error)
        encodable = encodable.replace("\x00", replacement)

    return "\"" + encodable.replace("\"", "\"\"") + "\""
            
def dict_factory(cursor, row):
    """ Dictionary factory for SQLite3 """

    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
