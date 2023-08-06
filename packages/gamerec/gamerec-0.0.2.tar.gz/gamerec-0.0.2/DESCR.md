**gamerec** is Python package intended to help process game recordings for 2 payers' games.  
File with game records can be loaded to Python collection object, be manipulated by user Python code,
and then be saved back to file. Current very limited version of package only supports Chess game 
and only .pgn file meta-data. 

Below is an example of package use to save games from .pgn file to SQLite database:
```python
from gamerec.storage.pgnfile.chess import ChessGameCollection as PGNChessGC
from gamerec.storage.sqlite.chess import ChessGameCollection as SQLiteChessGC

PGNFile = sys.argv[1]
SQLFile = sys.argv[2]

pgngc = PGNChessGC()
pgngc.load(PGNFile)
sqlgc = SQLiteChessGC()
sqlgc.data = pgngc.data
sqlgc.coding = "utf_8"
sqlgc.save(SQLFile)
```

Consider installing [normalizePGN](https://pypi.python.org/pypi/normalizePGN) which is an example of
how this package may be used.

For more information see files README.md and Changelog.md included in source-ball or 
in typical installation using pip deployed to folders:
- /usr/local/share/doc/gamerec (Linux)
- C:\Python35\doc\gamerec (Windows) or
- <USER>\AppData\Local\Programs\Python\Python35-32\Doc\gamerec
