# -*- coding: utf-8 -*-
#------------------------------------------------------------
# seriesly - XBMC Plugin
# https://github.com/plutec/seriesly_xbmc
#------------------------------------------------------------

import os,sys

try:
    import core
except:
    sys.path.append( os.path.abspath( os.path.join( os.path.dirname(__file__) , ".." ) ) )
