Development plans for future:
----------------------------------
Package could be extended in following directions:

- Port setup from distutils to newer setuptools.
- Add parsing Chess moves. This would allow to use package for thinks like 
  populating engines with moves and auto-commenting games (e.g. add best move candidates
  or positions' ranks, etc.).
- Add support for Chess960.
- Add support for other 2 players' games.
- Add support for some other input/output formats (e.g. SCID).
- ...

Unfortunately - I'm very sorry, but it does not look like I will have time for this in any near future :(.
But I welcome bug reports that should be reported in GitHub project page - for this I will try to find time :).

0.0.2 (2016.01.29):
----------------------------------
### Improvements
- Added pydoc documentation strings.
- Added few options to load() and save() methods.
- Added standard `setup.py` installation script. This means that package
  files can be installed from Python 3rd party package standard location. 
- Licensed `gamerec` under LGPLv3 license.
- Renamed package: gamelib -> gamerec.

0.0.1 (2012.10 - 2016.01):
----------------------------------
- Initial not-public release. Used privately.

