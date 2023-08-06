# -*- coding: utf-8 -*-
'''
This package contains generic classes for entire library.
'''

class Game:
    ''' Base class for games supported in this library. '''
    pass

class ChessGame (Game):
    ''' Class to support Chess Game. '''
    def __init__ (self):
        self.tags = dict()
        self.game = ""


########################################################################
from .config import *
__author__  = gamerec_author
__status__  = gamerec_status
__version__ = gamerec_version
__date__    = gamerec_date
