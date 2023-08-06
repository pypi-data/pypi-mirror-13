# -*- coding: UTF-8 -*-
'''
This package contains classes related to Chess Games storage in SQLite files.
This package uses configuration file: SQLiteChessGC.txt installed in user home folder - see README.md file.
'''

# Python standard libraries
import os, os.path, sqlite3

# This package modules
from gamerec import ChessGame
from gamerec.storage import GameCollection
from gamerec.config import gamerec_cfgfolder

# Sqlite Encoding names: http://sqlite.com/pragma.html#pragma_encoding
# Python Encoding names: file:///usr/share/doc/python3.2/html/library/codecs.html#standard-encodings
_dictSqlite2Python = {'UTF-8':'utf_8',
                      'UTF-16':'utf_16',
                      'UTF-16le':'utf_16_le',
                      'UTF-16be':'utf_16_be'
                     }
_dictPython2Sqlite = {}
for (sqlcode, pycode) in _dictSqlite2Python.items():
    _dictPython2Sqlite[pycode] = sqlcode


class ChessGameCollection (GameCollection):
    def __init__ (self):
        self.data = []
        self.coding = "utf_8"
        configfile = os.path.join(gamerec_cfgfolder(), "SQLiteChessGC.txt")
        if os.access(configfile, os.R_OK):
            self._loadconfig(configfile)
        else:
            self.tags = ["Event","Site","Date","Round","Board","White","Black","WhiteElo","BlackElo","TimeControl","Result"]
    
    def _loadconfig (self, filepath):
        """ Load configuration file """
        self.tags = []
        file = open(filepath, "r")
        for line in file:
            line = line.strip()
            if line.startswith("%"):
                continue
            if not line:
                continue
            self.tags.append(line)
        file.close()
    
    def load (self, filepath, sort = ""):
        """ Load the data from SQLite database.
        - filepath - path to sqlite database file
        - sort - place games in collection in given order (comma separated expression list as in ORDER BY)
        """ 
        self.data = []
        con = sqlite3.connect(filepath)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('PRAGMA encoding')
        row = cur.fetchone()
        self.coding = _dictSqlite2Python[row[0]]
        sql = 'SELECT * FROM Games'
        if len(sort) > 0:
            sql += ' ORDER BY ' + sort
        cur.execute(sql)
        while True:
            row = cur.fetchone()
            if row == None:
                break
            game = ChessGame()
            for field in row.keys():
                if field == "game":
                    game.game = row[field]
                elif field == "xxx":
                    tags = row[field].split('|')
                    for tag in tags:
                        if not tag == "":
                            tagv = tag.split('=')
                            game.tags[tagv[0]] = tagv[1]
                elif not row[field] == None:
                    game.tags[field] = row[field]
            self.data.append(game)
        con.close()
    
    def games_iterator(self):
        """ Iterator thru games collection """
        for game in self.data:
            lgame = game
            vals = []
            for tag in self.tags:
                if tag in lgame.tags:
                    vals.append(lgame.tags[tag])
                    del lgame.tags[tag]
                else:
                    vals.append(None)
            xxx = ""
            for (tag, val) in lgame.tags.items():
                xxx += "{0}={1}|".format(tag, val)
            vals.append(xxx)
            vals.append(lgame.game)
            yield tuple(vals)
        
    def save (self, filepath, cleargames = False):
        """ Saves the data to SQLite database.
        - filepath - path to sqlite database file
        - cleargames - clear database before adding games
        """ 
        existingDb = os.access(filepath, os.R_OK + os.W_OK)
        con = sqlite3.connect(filepath)
        if not existingDb:
            if not self.coding == "utf_8":
                if self.coding in _dictPython2Sqlite:
                    coding = _dictPython2Sqlite[self.coding]
                else:
                    raise RuntimeError("SQLiteGameCollection.save: Unsupported coding \"{}\"".format(self.coding))
                con.execute('PRAGMA encoding="{0}"'.format(coding))
            sql = "CREATE TABLE IF NOT EXISTS Games("
            for tag in self.tags:
                sql += tag + ","
            sql += "xxx,game)"
            con.execute(sql)
            con.commit()
        elif cleargames:
            con.execute('DELETE FROM Games')
            con.commit()
        if len(self.data) > 0:
            sql = "INSERT INTO Games VALUES(" + "?," * (len(self.tags)+1) + "?)"
            #print("sql=",sql)
            con.executemany(sql, self.games_iterator())
            con.commit()
         