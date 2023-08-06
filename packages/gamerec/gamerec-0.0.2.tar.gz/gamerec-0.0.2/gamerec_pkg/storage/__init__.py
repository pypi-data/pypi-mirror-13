# -*- coding: utf-8 -*-
'''
This package contains classes related to games' collection storage.
'''

from collections import UserList

class GameCollection (UserList):
    """ Base class for concrete containers that are collection of 2 palyers' games """

    def load (self, source):
        ''' Load the data from source which can point to file or database locator or any other resource '''
        raise NotImplementedError

    def save (self, dest):
        ''' Saves the data to dest which can point to file or database locator or any other resource '''
        raise NotImplementedError


########################################################################
from gamerec.config import *
__author__  = gamerec_author
__status__  = gamerec_status
__version__ = gamerec_version
__date__    = gamerec_date
