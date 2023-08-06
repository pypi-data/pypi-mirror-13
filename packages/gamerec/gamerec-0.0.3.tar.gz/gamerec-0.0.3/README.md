Gamerec
========

Library to process 2 players' games recordings (only chess now).

Works only with Python 3.  
Tested only on Linux and Windows 7.  
For package description see DESCR.md file.

INSTALLATION (System wide - for all users):
-------------------------------------------

### Installation Method 1
Recommended method for installation of this package is from Python Package Index:  
Linux: `sudo pip3 install gamerec`  
Windows: `pip3 install gamerec`

### Installation Method 2
If you want to install particular version, download source-ball and issue:  
Linux: `sudo pip3 install gamerec-<ver>.tar.gz`  
Windows: `pip3 install gamerec-<ver>.tar.gz`

### Installation Method 3
Alternatively unpack source-ball and from unpacked folder run command:  
Linux: `sudo python3 setup.py install`  
Windows: `python setup.py install`  
Note: More installation options are possible - see documentation of Python `distutils` package.

### Installation from Source
If you have downloaded archive snapshot, first unpack it and from root folder run command: 
`python3 setup.py sdist` 
which will create `dist` subfolder and create source-ball in it. Then apply method 2 or 3 above.

### Files deployed by installation script
- `gamerec` package and its sub-packages 
- Documentation:  
  Linux: `<PREFIX>/share/doc/gamerec/*`, where `<PREFIX>` is by default `/usr/local`  
  Windows: `<PREFIX>\Doc\gamerec\*`, where `<PREFIX>` is by default `C:\Python35` or `<USER>\AppData\Local\Programs\Python\Python35-32`
- Configuration:  
  Linux: `<USER>/.config/gamerec/*`, where `<USER>` is user home folder  
  Windows: `<USER>\AppData\Local\gamerec\*`, where `<USER>` is user profile folder

RE-INSTALLATION/UPGRADE:
------------------------

To upgrade packages from PyPi use -U option:
`[sudo] pip install -U gamerec`.  

USAGE:
------

Please refer to  deployed documentation and Pydoc accesible information contained in this package.  

### Obtaining Pydoc information: 
Run conmand:  
Linux: `pydoc -g`  
Windows: Start Menu/Python/Module Docs  
and then press 'Open Browser' or manually navigate to given URL.
Note: this URL does not work with Windows IE browser. 
Then go to below sections (near bottom of page):  
Linux: `/usr/local/lib/python3.5/dist-packages/`  
Windows: `<PYTHON>\lib\site-packages`  
and go into `gamerec(package)` link.
