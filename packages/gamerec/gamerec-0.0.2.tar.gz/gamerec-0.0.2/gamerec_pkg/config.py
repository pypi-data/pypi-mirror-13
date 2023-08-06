"""This module contains package meta information and common functions."""

from os import name
from os.path import join, expanduser

# Set version number here
gamerec_author  = "Grzegorz Wierzchowski <gwierzchowski@wp.pl>"
gamerec_status  = '4 - Beta'
gamerec_version = '0.0.2'
gamerec_date    = '2016 January'

#Development Status :: 1 - Planning
#Development Status :: 2 - Pre-Alpha
#Development Status :: 3 - Alpha
#Development Status :: 4 - Beta
#Development Status :: 5 - Production/Stable
#Development Status :: 6 - Mature
#Development Status :: 7 - Inactive

def gamerec_cfgfolder():
    if name == 'posix':
        return join(expanduser("~"), ".config", "gamerec")
    if name == 'nt':
        return join(expanduser("~"), "AppData", "Local", "gamerec")
    return join(expanduser("~"), ".gamerec")
