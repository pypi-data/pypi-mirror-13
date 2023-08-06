# -*- coding: UTF-8 -*-
'''
This package contains classes related to Chess Games storage in .pgn files.
This package uses configuration file: PGNChessGC.pgn installed in user home folder - see README.md file.
'''

# Python standard libraries
import re, os, os.path

# This package modules
from gamerec import ChessGame
from gamerec.storage import GameCollection
from gamerec.config import gamerec_cfgfolder

# Vi Encoding names: http://vimdoc.sourceforge.net/htmldoc/mbyte.html#encoding-names
# Python Encoding names: file:///usr/share/doc/python3.2/html/library/codecs.html#standard-encodings
_dictVi2Python = {'latin1':'latin_1',
                  'iso-8859-1':'latin_1',
                  'iso-8859-2':'iso8859_2',
                  'cp1250':'cp1250',
                  'utf-8':'utf_8',
                  'utf-16':'utf_16',
                  'utf-16 le':'utf_16_le',
                  'utf-16 be':'utf_16_be'
                 } #TODO: Finish this list.
_dictPython2Vi = {}
for (vicode, pycode) in _dictVi2Python.items():
    _dictPython2Vi[pycode] = vicode

# Vim modelines: http://vimdoc.sourceforge.net/htmldoc/options.html#modeline
_coding1re = re.compile(r"%\s+(?:vi:|vim:|ex:)\s*[\w\s:=]*(?:enc|encoding)=(\w[\w\-]*)[\w\s:=]*")

# Below RE for PGN file are kindly borrowed from http://www.pychess.org/ program (version 0.10.1).
# Many thanks to PyChess project !
_tagre = re.compile(r"\[([a-zA-Z]+)[ \t]+\"(.*?)\"\]")
_comre = re.compile(r"(?:\{.*?\})|(?:;.*?[\n\r])|(?:\$[0-9]+)", re.DOTALL)
_movre = re.compile(r"""
    (                   # group start
    (?:                 # non grouping parenthesis start
    [KQRBN]?            # piece
    [a-h]?[1-8]?        # unambiguous column or line
    x?                  # capture
    [a-h][1-8]          # destination square
    =?[QRBN]?           # promotion
    |O\-O(?:\-O)?       # castling
    |0\-0(?:\-0)?       # castling
    )                   # non grouping parenthesis end
    [+#]?               # check/mate
    )                   # group end
    [\?!]*              # traditional suffix annotations
    \s*                 # any whitespace
    """, re.VERBOSE)

# token categories
COMMENT_REST, COMMENT_BRACE, COMMENT_NAG, \
VARIATION_START, VARIATION_END, \
RESULT, FULL_MOVE, MOVE_COUNT, MOVE, MOVE_COMMENT = range(1,11)

_pattern = re.compile(r"""
    (\;.*?[\n\r])        # comment, rest of line style
    |(\{.*?\})           # comment, between {} 
    |(\$[0-9]+)          # comment, Numeric Annotation Glyph
    |(\()                # variation start
    |(\))                # variation end
    |(\*|1-0|0-1|1/2)    # result (spec requires 1/2-1/2 for draw, but we want to tolerate simple 1/2 too)
    |(
    ([0-9]{1,3}\s*[.]*\s*)?
    ([a-hxOoKQRBN1-8+#=]{2,7}
    |O\-O(?:\-O)?
    |0\-0(?:\-0)?)
    ([\?!]{1,2})*
    )    # move (full, count, move with ?!, ?!)
    """, re.VERBOSE | re.DOTALL)


class ChessGameCollection (GameCollection):
    '''Class to load and save Chess Game Collection in .pgn file.'''
    def __init__ (self):
        self.data = []
        self.coding = "latin_1"
        templatefile = os.path.join(gamerec_cfgfolder(), "PGNChessGC.pgn")
        if os.access(templatefile, os.R_OK):
            self._loadtemplate(templatefile)
        else:
            self.tags = ["Event","Site","Date","Round","White","Black","Result"]
            self.addtagspos = 6  #set to -1 for not placing additional tags
            self.gameformat = ""
    
    def _loadtemplate (self, filepath):
        """ Load file in PGN format and treat it as save template (order of tags)"""
        self.tags = []
        self.addtagspos = -1
        self.gameformat = ""
        file = open(filepath, "r")
        for line in file:
            line = line.lstrip()
            if line.startswith("%"):
                continue
            if not line:
                continue
            if line.startswith("["):
                tagmatch = _tagre.match(line)
                if tagmatch is not None:
                    if tagmatch.group(1) == "xxx":
                        self.addtagspos = len(self.tags)
                    else:
                        self.tags.append(tagmatch.group(1))
                continue
            self.gameformat += line
            break
        file.close()
    
    def load (self, filepath):
        """ Load the data from file in PGN format """
        self.data = []
        self.coding = "latin_1"
        codingKnown = False
        while True:
            file = open(filepath, "r", encoding=self.coding)
            codingChanged = False
            mode = 0 #0-begin/aftergame 1-tags 2-gametext
            game = ChessGame()
            for line in file:
                line = line.lstrip()
                if line.startswith("%"):
                    if not codingKnown:
                        codingmatch = _coding1re.match(line)
                        if codingmatch is not None:
                            if codingmatch.group(1) in _dictVi2Python:
                                self.coding = _dictVi2Python[codingmatch.group(1)]
                            else:
                                self.coding = codingmatch.group(1)
                            codingChanged = True
                            codingKnown = True
                            break
                    continue
                if mode != 2 and line.startswith("["):
                    codingKnown = True
                    mode = 1
                    tagmatch = _tagre.match(line)
                    if tagmatch is not None:
                        game.tags[tagmatch.group(1)] = tagmatch.group(2)
                    continue
                if not line:
                    if mode == 0:
                        pass
                    elif mode == 1:
                        pass
                    else:
                        self.data.append(game)
                        game = ChessGame()
                        mode = 0
                    continue
                game.game += line
                mode = 2
            if mode == 2:
                self.data.append(game)
            file.close()
            if not codingChanged:
                break
    
    def save (self, filepath, opmode = "a"):
        """ Saves the data to file in PGN format.
        Use opmode as file open flag (i.e. append to file or overwrite).
        """
        file = open(filepath, opmode, encoding=self.coding)
        if not self.coding == "latin_1":
            if self.coding in _dictPython2Vi:
                coding = _dictPython2Vi[self.coding]
            else:
                coding = self.coding
            print("% vi: encoding={0}\n".format(coding), file = file)
        for game in self.data:
            gametags = dict(game.tags)
            tags = []
            for tag in self.tags:
                if tag in gametags:
                    tags.append("[{0} \"{1}\"]".format(tag, gametags[tag]))
                    del gametags[tag]
                else:
                    tags.append("[{0} \"?\"]".format(tag))
            if self.addtagspos == -1:
                for tag in tags:
                    print(tag, file = file)
            else:
                for tag in tags[0:self.addtagspos]:
                    print(tag, file = file)
                for (tag, val) in gametags.items():
                    print("[{0} \"{1}\"]".format(tag, val), file = file)
                for tag in tags[self.addtagspos:]:
                    print(tag, file = file)
            print("", file = file)
            print(game.game, file = file)
        file.close()
         