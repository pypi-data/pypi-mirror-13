#!/usr/bin/env python3

# This is only for Python 2.7
from __future__ import print_function

import os, sys
import distutils.core, distutils.file_util

sys.path.insert(0, '.')
from gamerec_pkg.config import *


if os.name == 'posix':
    doclocation = 'share/doc/gamerec'
else:
    doclocation = 'doc/gamerec'

cfglocation = gamerec_cfgfolder()

with open('DESCR.md') as f:
    long_description = f.read()

dist = distutils.core.setup(name = 'gamerec',
    version = gamerec_version,
    description = "Library to process 2 players' games recordings (only chess now)",
    long_description = long_description,
    author = 'Grzegorz Wierzchowski',
    author_email = 'gwierzchowski@wp.pl',
    url = 'https://github.com/gwierzchowski/gamerec',
    packages = ['gamerec','gamerec.storage','gamerec.storage.pgnfile','gamerec.storage.sqlite'],
    package_dir = {'gamerec': 'gamerec_pkg'},
    data_files = [(doclocation, ['README.md', 'LICENSE.txt', 'DESCR.md', 'docs/Changelog.md']),
                  (cfglocation, ['conf/PGNChessGC.pgn', 'conf/SQLiteChessGC.txt'])],
    license = 'LGPLv3',
    platforms = 'any',
    classifiers = [
        'Development Status :: ' + gamerec_status,
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
    )

if sys.argv[1] in ['install']:
    # Unfotunately while installing using pip those print statements does not work on Windows
    print ('---------------------------------------------------------')
    isobj = dist.get_command_obj('install_data')
    readmedoc = None
    for doc in isobj.get_outputs():
        if 'README.md' in doc:
            readmedoc = doc
            break
    if readmedoc:
        print ('See %s file' % readmedoc)
    else:
        print ('See files deployed to documentation folder')
    print ('---------------------------------------------------------')
