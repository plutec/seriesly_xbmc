# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Logger multiplataforma
#------------------------------------------------------------
# pelisalacarta
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
# Creado por: Jesús (tvalacarta@gmail.com)
# Licencia: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
#------------------------------------------------------------
# Historial de cambios:
# Modified by plutec for adding loggeractive via config
#------------------------------------------------------------

import platformcode.xbmc.logger as platformlogger
default = False

from core import config2 as config

loggeractive = config.get_setting('debug')=='true'

def log_enable(active):
    global loggeractive
    loggeractive = active

def info(texto):
    if loggeractive:
        if not default:
            platformlogger.info(texto)
        else:
            print texto

def debug(texto):
    if loggeractive:
        if not default:
            platformlogger.info(texto)
        else:
            print texto

def error(texto):
    if loggeractive:
        if not default:
            platformlogger.info(texto)
        else:
            print texto
