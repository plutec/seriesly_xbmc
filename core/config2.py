# -*- coding: utf-8 -*-
#import xbmcplugin
import xbmcaddon
import xbmc

PLUGIN_NAME = "seriesly"
__settings__ = xbmcaddon.Addon(id="plugin.video."+PLUGIN_NAME)

def open_settings():
    __settings__.openSettings()


def is_configured():
    username = __settings__.getSetting('username')
    password = __settings__.getSetting('password')
    if username != '' and password != '':
        return True
    return False

def get_setting(name):
    dev = __settings__.getSetting(name)
    return dev

def set_setting(name,value):
    __settings__.setSetting(name, value)

def launch():
    open_settings()

def get_localized_string(code):
    dev = xbmc.getLocalizedString( code )
    
    try:
        dev = dev.encode("utf-8") #This only aplies to unicode strings. The rest stay as they are.
    except:
        pass
    
    return dev