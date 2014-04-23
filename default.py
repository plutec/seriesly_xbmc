# -*- coding: utf-8 -*-
#------------------------------------------------------------
# series.ly
#------------------------------------------------------------


# Constants
__plugin__  = "series.ly"
__author__  = "Antonio S. (plutec.net) asanchez@plutec.net"
__url__     = "http://plutec.net"
__date__    = "14 Abril 2014"
__version__ = "0.7"


import os
import sys
from core import config
from core import logger

logger.info("[default.py] seriesly init...")

libraries = xbmc.translatePath( os.path.join( config.get_runtime_path(), 'lib/'))
#bspath = os.path.join(os.path.dirname(os.path.realpath(__file__)),"lib/")
sys.path.append(libraries)

# Runs xbmc launcher
from core import launcher
launcher.run()
