# -*- coding: utf-8 -*-
#------------------------------------------------------------
# seriesly
# XBMC Plugin
# Code of tvalacarta
#------------------------------------------------------------

import re
import os
import sys
#import scrapertools
import time
import config
import logger
import xbmcgui
import xbmcplugin
import settings
import requests
import ziptools

PLUGIN_NAME = "seriesly"

ROOT_DIR = config.get_runtime_path()

REMOTE_VERSION_FILE = 'https://raw2.github.com/plutec/seriesly_xbmc/master/version.xml'

DESTINATION_FOLDER = ROOT_DIR #config.get_runtime_path()
REMOTE_FILE = 'https://github.com/plutec/seriesly_xbmc/blob/master/downloads/seriesly_xbmc.zip?raw=true'
LOCAL_VERSION_FILE = os.path.join( ROOT_DIR , "version.xml")

LOCAL_FILE = os.path.join( ROOT_DIR , '..', PLUGIN_NAME+"-" )

def launch():
    if checkforupdates():
        #Pasamos a descargar
        update()

def checkforupdates():
    logger.info("[updater.py] checkforupdates")

    # Descarga el fichero con la versión en la web
    logger.info("[updater.py] Verificando actualizaciones...")
    logger.info("[updater.py] Version remota: "+REMOTE_VERSION_FILE)
    #data = scrapertools.cachePage( REMOTE_VERSION_FILE )
    response = requests.get(url=REMOTE_VERSION_FILE)
    data = response.text
    #logger.info("xml descargado="+data)
    patronvideos  = '<tag>([^<]+)</tag>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    #scrapertools.printMatches(matches)
    versiondescargada = matches[0]
    logger.info("[updater.py] version descargada="+versiondescargada)
    
    # Lee el fichero con la versión instalada
    localFileName = LOCAL_VERSION_FILE
    logger.info("[updater.py] Version local: "+localFileName)
    infile = open( localFileName )
    data = infile.read()
    infile.close()
    #logger.info("xml local="+data)
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    #scrapertools.printMatches(matches)
    versionlocal = matches[0]
    logger.info("[updater.py] version local="+versionlocal)

    arraydescargada = versiondescargada.split(".")
    arraylocal = versionlocal.split(".")
    
    if len(arraylocal) == len(arraydescargada):
        #logger.info("caso 1")
        hayqueactualizar = False
        for i in range(0, len(arraylocal)):
            if int(arraydescargada[i]) > int(arraylocal[i]):
                hayqueactualizar = True

    if len(arraylocal) > len(arraydescargada):
        #logger.info("caso 2")
        hayqueactualizar = False
        for i in range(0, len(arraydescargada)):
            #print arraylocal[i], arraydescargada[i], int(arraydescargada[i]) > int(arraylocal[i])
            if int(arraydescargada[i]) > int(arraylocal[i]):
                hayqueactualizar = True
    
    if len(arraylocal) < len(arraydescargada):
        #logger.info("caso 3")
        hayqueactualizar = True
        for i in range(0, len(arraylocal)):
            #print arraylocal[i], arraydescargada[i], int(arraylocal[i])>int(arraydescargada[i])
            if int(arraylocal[i]) > int(arraydescargada[i]):
                hayqueactualizar =  False
            elif int(arraylocal[i]) < int(arraydescargada[i]):
                hayqueactualizar =  True
                break

    if hayqueactualizar:
        logger.info("[updater.py] actualizacion disponible")
        
        # Añade al listado de XBMC
        """

        listitem = xbmcgui.ListItem( "Descargar version "+versiondescargada, iconImage=os.path.join(IMAGES_PATH, "poster" , "Crystal_Clear_action_info.png"), thumbnailImage=os.path.join(IMAGES_PATH, "Crystal_Clear_action_info.png") )
        itemurl = '%s?action=update&version=%s' % ( sys.argv[ 0 ] , versiondescargada )
        import xbmcplugin
        xbmcplugin.addDirectoryItem( handle = int(sys.argv[ 1 ]), url = itemurl , listitem=listitem, isFolder=True)
        """
        # Avisa con un popup
        dialog = xbmcgui.Dialog()
        dialog.ok(u"Versión %s disponible" % versiondescargada,
            u"Se va a actualizar el plugin a la versión %s" % versiondescargada)
        return True
    else:
        # Avisa con un popup
        dialog = xbmcgui.Dialog()
        dialog.ok(u"Plugin actualizado",
            u"El plugin ya se encuentra en la última versión %s" % versiondescargada)
    return False
    
def update():
    # Descarga el ZIP
    logger.info("[updater.py] update")
    remotefilename = REMOTE_FILE #+params.get("version")+".zip"
    localfilename = LOCAL_FILE #+params.get("version")+".zip"
    logger.info("[updater.py] remotefilename=%s" % remotefilename)
    logger.info("[updater.py] localfilename=%s" % localfilename)
    logger.info("[updater.py] descarga fichero...")
    inicio = time.clock()

    response = requests.get(url=remotefilename, stream=True)
    fd = open(localfilename, 'wb')
    fd.write(response.raw.read())
    fd.close()
    
    fin = time.clock()
    logger.info("[updater.py] Descargado en %d segundos " % (fin-inicio+1))
    
    # Lo descomprime
    logger.info("[updater.py] descomprime fichero...")

    unzipper = ziptools.ziptools()
    destpathname = DESTINATION_FOLDER
    logger.info("[updater.py] destpathname=%s" % destpathname)
    unzipper.extract(localfilename,destpathname)
    
    # Borra el zip descargado
    logger.info("[updater.py] borra fichero...")
    os.remove(localfilename)

    dialog = xbmcgui.Dialog()
    dialog.ok("Actualizada", "Se ha actualizado correctamente")
