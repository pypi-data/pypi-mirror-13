#!C:\Python35\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'gmusicapi-scripts==0.2.0','console_scripts','gmdownload'
__requires__ = 'gmusicapi-scripts==0.2.0'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('gmusicapi-scripts==0.2.0', 'console_scripts', 'gmdownload')()
    )
