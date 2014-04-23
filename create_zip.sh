#!/bin/sh

find . -name "*.pyc" -exec rm -rf {} \;

zip -r seriesly_xbmc.zip addon.xml default.py LICENSE channelselector.py icon.png players core __init__.py  README.md lib resources version.xml 
