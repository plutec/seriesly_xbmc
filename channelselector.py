# -*- coding: utf-8 -*-
import urlparse,urllib2,urllib,re
import os
import sys
#from core import scrapertools
#from core import config
from core import config2 as config
from core import logger
from core.item import Item
from core import api_sly
#from core import settings
import xbmcgui
import xbmcplugin
import xbmc

from players import tools as players_tools
from players import PlayedTo
from players import Allmyvideos
from players import MagnoVideo
from players import VidSpot
from players import StreamCloud

import collections

import CommonFunctions
#common.plugin = plugin

DEBUG = True
CHANNELNAME = "channelselector"


def serialize(input):
    to_ret = ''
    for key, value in input.iteritems():
        if not isinstance(value, int):
            to_ret += '&%s=%s' % (key, value) #TODO vaya megda
        else:
            to_ret += '&%s=%s' % (key, value)
    return to_ret

def my_series(params, url, category):
    logger.info("channelselector.my_series")
    API = api_sly.APISLY(username=config.get_setting('username'),
                         password=config.get_setting('password'), 
                         force=True)
    series = API.my_series()
    for serie in series:
        logger.info(repr(serie))
        channelname = {'mediaType':serie['mediaType'], 'id':serie['id']} #Params to define a serie
        addfolder(name=serie['name'] , channelname=serialize(channelname) , action="serie_seasons",
            thumbnail=serie['image'])

    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

def my_movies(params, url, category):
    logger.info("channelselector.my_movies")
    API = api_sly.APISLY(username=config.get_setting('username'),
                     password=config.get_setting('password'), 
                     force=True)
    movies = API.my_movies()
    for movie in movies:
        logger.info(repr(movie))
        channelname = {'mediaType':movie['mediaType'], 
                        'idMedia':movie['id2'], 
                        'status':movie['status'],
                        'idm': movie['idm']} #Params to define a movie
        title = '%s [%s]' % (movie['name'], 
                             API.media_status(mediaType=movie['mediaType'], 
                                         status=movie['status']))
        addfolder(name=title,
                  channelname=serialize(channelname), 
                  action="details",
                  thumbnail=movie['image'])

    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )


def series_seasons(params, url, category):
    logger.info('channelselector.chapters')
    API = api_sly.APISLY(username=config.get_setting('username'),
                         password=config.get_setting('password'), 
                         force=True)
    #Needed mediaType and id_media
    logger.info(repr(params))
    #params = {'category': '', 'mN': 'The Big Bang Theory', 'id2': '589', 'nE': '169', 'mT': '1', 'action': 'serie_seasons', 'nS': '7', 'id': '2V675K5Y2R', 'channel': ''}
    
    seasons = API.get_serie_info(mediaType=params['mediaType'], id=params['id'])
    
    episodes = seasons['episodes']
    
    params = {'mediaType': params['mediaType'], 'id':params['id']}
    od = collections.OrderedDict(sorted(episodes.items()))
    for i in od.iterkeys():
        params['season'] = i
        addfolder(name="Temporada %s" % i, 
                  channelname=serialize(params), 
                  action='chapters')
    
    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

def view_video(params, url, category):
    logger.info('channelselector.view_video')
    API = api_sly.APISLY(username=config.get_setting('username'),
                         password=config.get_setting('password'), 
                         force=True)
    logger.info("PARAMS: %s" % repr(params))
    url = ''
    if params['host'] == 'Played.to':
        url_host = API.get_video_link(idVideo=params['idVideo'], mediaType=params['mediaType'])
        logger.info("PLAYEDTO: %s" % url_host)
        url = PlayedTo.get_video_by_url(url_host)
        logger.info("PLAYEDTO2: %s" % url)
    elif params['host'] == 'allmyvideos':
        url_host = API.get_video_link(idVideo=params['idVideo'], mediaType=params['mediaType'])
        logger.info("ALLMYVIDEOS: %s" % url_host)
        url = Allmyvideos.get_video_by_url(url_host)
        logger.info("ALLMYVIDEOS2: %s" % url)
    elif params['host'] == 'Magnovideo':
        url_host = API.get_video_link(idVideo=params['idVideo'], mediaType=params['mediaType'])
        logger.info("MAGNOVIDEO: %s" % url_host)
        url = MagnoVideo.get_video_by_url(url_host)
        logger.info("MAGNOVIDEO2: %s" % url)
    elif params['host'] == 'Vidspot':
        url_host = API.get_video_link(idVideo=params['idVideo'], mediaType=params['mediaType'])
        logger.info("VIDSPOT: %s" % url_host)
        url = VidSpot.get_video_by_url(url_host)
        logger.info("VIDSPOT2: %s" % url)
    elif params['host'] == 'StreamCloud':
        url_host = API.get_video_link(idVideo=params['idVideo'], 
                                      mediaType=params['mediaType'])
        logger.info("StreamCloud: %s" % url_host)
        url = StreamCloud.get_video_by_url(url_host)
        logger.info("Streamcloud2: %s" % url)

    addvideo(name='Ver', url=url)
    params['report'] = 1
    #addfolder(name='Reportar', channelname=serialize(params), action='report')
    finish_video_list()

def report_link(params, url, category):
    logger.info('channelselector.report_link')
    logger.info(repr(params))

def series_chapters(params, url, category):
    logger.info('channelselector.series_chapter')
    API = api_sly.APISLY(username=config.get_setting('username'),
                         password=config.get_setting('password'), 
                         force=True)
    
    seasons = API.get_serie_info(id=params['id'], mediaType=params['mediaType'])
    #logger.info(repr(seasons))
    episodes = seasons['episodes'][params['season']]
    for episode in episodes:
        title = '%sx%s - %s' % (episode['season'], episode['episode'], 
                                episode['title'])
        if episode.has_key('viewed'):
            pass
            #title += ' |            Visto'
        params = {'idMedia':episode['idc'], 
                  'mediaType':episode['mediaType']}

        logger.info("EPISODE %s" % str(episode))
        if episode.has_key('viewed'):
            addfolder(name=title, channelname=serialize(params), action='links', watched=True)
        else:
            addfolder(name=title, channelname=serialize(params), action='links')

    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

def show_links(params, url, category):
    logger.info('channelselector.show_links')
    logger.info('PARAMS: %s' % params)
    API = api_sly.APISLY(username=config.get_setting('username'),
                         password=config.get_setting('password'), 
                         force=True)

    try:
        del params['title'] #Prevent unicode/ascii problems
    except:
        pass

    if int(params['mediaType']) == api_sly.SERIE:
        logger.info("ENTRASERIE")
        links = API.get_links(idm=params['idMedia'], 
                          mediaType=params['mediaType'])
    elif int(params['mediaType']) == api_sly.MOVIE:
        links = API.get_links(idm=params['idm'], 
                          mediaType=params['mediaType'])

    count = 0
    if params.has_key('number'):
        count = int(params['number'])
        links = links[count:]

    for link in links:
        not_available = False
        url = ''
        
        if link['linksType'] == 'streaming':
            logger.info("LINK: %s" % repr(link))
            quality = link['quality']
            if link.has_key('features'):
                quality += ' ' + link['features']
            title = '%s | %s | %s' % (link['lang'], quality, link['host'])
            if not players_tools.available_player(link['host']):
                title += ' | Reproductor NO DISPONIBLE' 
            params['idVideo'] = link['idVideo']
            params['host'] = link['host']
            if not_available:
                title += ' | No disponible'
                addfolder(name=title, channelname=params, action=params['action'])
            else:
                addfolder(name=title, channelname=params, action='view_video')
   
    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )
    

def change_status(params, url, category):
    logger.info('channelselector.change_status')
    API = api_sly.APISLY(username=config.get_setting('username'),
                         password=config.get_setting('password'), 
                         force=True)
    logger.info('PARAMS %s' % repr(params))
    if params.has_key('new_status'):
        params['status'] = params['new_status']
        logger.info("VIENE PARA CAMBIARLO")
        
        API.change_status(idm=params['idm'], 
                          mediaType=params['mediaType'], 
                          newStatus=params['new_status'])
        
        logger.info("newSTATUS: %s" % params['new_status'])
        """
        params = {
        'action': 'change_status', 
        'category': 'Cambiar estado', 
        'idm': '12481', 
        'mediaType': '2', 
        'channel': ''
        }
        """
    status = [1, 2, 3]
    #First, actual status
    params['new_status'] = params['status']
    title = '%s | Actual' % API.media_status(params['status'])
    addfolder(name=title, channelname=params, action='details')
    status.remove(int(params['status']))
    #Then, the rest
    for i in status:
        params['new_status'] = i
        addfolder(name=API.media_status(i), channelname=params, action='change_status')

    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

def serie_details_old(params, url, category):
    #TODO: Funciona esto?
    logger.info('channelselector.serie_details_old')
    API = api_sly.APISLY(username=config.get_setting('username'),
                         password=config.get_setting('password'), 
                         force=True)
    logger.info('PARAMS %s' % repr(params))
    

    #Pelis
    """
    params = {
            'action': 'details',
            'category': '',
            'idm': '12654',
            'mediaType': '2',
            'channel': ''
        }
    """
    params = {'mediaType':params['mediaType'], 'idm':params['idm']}
    addfolder(name='Info (En desarrollo)', channelname=serialize(params), action='')
    addfolder(name='Trailer (En desarrollo)', channelname=serialize(params), action='')
    addfolder(name='Relacionadas (En desarrollo)', channelname=serialize(params), action='')
    addfolder(name='Criticas (En desarrollo)', channelname=serialize(params), action='')
    #addfolder(name='Cambiar estado', channelname=serialize(params), action='change_status')
    addfolder(name='Enlaces', channelname=serialize(params), action='links')

    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )


def film_details(params, url, category):
    #FILM DETAILS (Información, trailer, relacionadas, críticas, enlaces)
    #TODO
    logger.info('channelselector.film_details')
    
    logger.info('PARAMS %s' % repr(params))
    
    """
    params = {
            'mediaType':params['mediaType'], 
            'idMedia':params['idMedia'],
            #'idm':params['idm']
            }
    """
    addfolder(name='Info (En desarrollo)', channelname=serialize(params), action='details')
    addfolder(name='Trailer (En desarrollo)', channelname=serialize(params), action='details')
    addfolder(name='Relacionadas (En desarrollo)', channelname=serialize(params), action='details')
    addfolder(name='Criticas (En desarrollo)', channelname=serialize(params), action='details')
    addfolder(name='Cambiar estado (En desarrollo)', channelname=serialize(params), action='details')#'change_status')
    addfolder(name='Enlaces', channelname=serialize(params), action='links')

    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

def most_valuated_series(params, url, category):
    #Tested
    logger.info('channelselector.most_valuated_series')
    API = api_sly.APISLY(username=config.get_setting('username'),
                         password=config.get_setting('password'), 
                         force=True)
    
    series = API.get_most_valuated(mediaType=api_sly.SERIE)
    #logger.info("DATA %s" % repr(series))
    for media in series:
        addfolder(name=media['name'], channelname=serialize(media), 
                  action='serie_seasons', thumbnail=media['thumbnail'])

    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )


def most_valuated_movies(params, url, category):
    #TODO Developing
    logger.info('channelselector.most_valuated_movies')
    API = api_sly.APISLY(username=config.get_setting('username'),
                         password=config.get_setting('password'), 
                         force=True)
    
    movies = API.get_most_valuated(mediaType=api_sly.MOVIE)
    #logger.info("DATA %s" % repr(series))
    for media in movies:
        addfolder(name=media['name'], channelname=serialize(media), 
                  action='details', thumbnail=media['thumbnail'])

    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

"""
Procedimiento de búsqueda de contenido.
"""
def search(params, url, category):
    
    logger.info('channelselector.search')
    API = api_sly.APISLY(username=config.get_setting('username'),
                         password=config.get_setting('password'), 
                         force=True)
    query = CommonFunctions.getUserInput("Buscar", '')
    #logger.info("QUERY: %s"% query)

    if not query or query == '':
        return
    
    search = API.search(search_term=query)
    logger.info("SEARCHRESULT %s" % search)
    for item in search:
        if item.has_key('title') and item.has_key('mediaType') and item.has_key('idm'):
            params = {'title': item['title'],
                      'mediaType':item['mediaType'], 
                      'idm' : item['idm']}
            if item.has_key('idMedia'):
                params['idMedia'] = item['idMedia']
            title = item['title']
            if item.has_key('year'):
                title = '%s [%s]' % (item['title'], item['year'])
            thumbnail = item.get('img', '').replace(' ','')
            addfolder(name=title, 
                      channelname=serialize(params), 
                      action='details',
                      thumbnail=thumbnail)

    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

"""
Desconectar usuario.
Post:
    Elimina el usuario y la password de la configuración.
"""
def logout(params, url, category):
    logger.info('channelselector.logout')
    config.set_setting('username', '')
    config.set_setting('password', '')

def mainlist(params,url,category):
    logger.info("channelselector.mainlist")
    if not config.is_configured():
        config.open_settings()

    now_in_channel = 'main'
    addfolder("Buscar" , 'main' , "search") # , thumbnailname=elemento.thumbnail, folder=elemento.folder)
    addfolder("Mis series" , 'main' , "my_series")
    addfolder("Mis pelis" , 'main' , "my_movies")
    addfolder('Series más vistas' , 'main' , 'most_valuated_series')
    addfolder('Pelis más vistas' , 'main' , 'most_valuated_movies')
    addfolder("Cerrar sesión (%s)" % config.get_setting('username'), 
                                                        'main' , 'logout')
    addfolder("Actualizar plugin" , 'main' , "update_plugin")
    addfolder("Configuración" , 'main' , "configuration")
    # Label (top-right)...

    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )


def addvideo(name, url, thumbnailImage=None, iconImage=None):
    if not iconImage:
        iconImage = 'DefaultVideo.png'
    if not thumbnailImage:
        thumbnailImage = iconImage

    li = xbmcgui.ListItem(name, iconImage=iconImage, thumbnailImage=thumbnailImage)
    li.setInfo(type='video', infoLabels={'Title':name})
    #li.setThumbnailImage(thumbnailImage)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li)

def finish_video_list():
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def addfolder(name, channelname, action, category="", thumbnail='', folder=True, watched=None):
    #TODO CAMBIAR Thumbnails
    if category == "":
        try:
            category = unicode( name, "utf-8" ).encode("iso-8859-1")
        except:
            pass

    if isinstance(channelname, dict):
        channelname = serialize(channelname)
    if watched:
        listitem = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
        listitem.setInfo(type='video', infoLabels={'PlayCount':1, 'Overlay': 1})
    else:
        listitem = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
    itemurl = '%s?channel=%s&action=%s&category=%s' % ( sys.argv[ 0 ] , channelname , action , category )
    xbmcplugin.addDirectoryItem( handle = int(sys.argv[ 1 ]), url = itemurl , listitem=listitem, isFolder=folder)


def dialog(): 
    #TODO
    pDialog = xbmcgui.DialogProgress()
    ret = pDialog.create('pelisalacarta', 'Añadiendo episodios...')
    pDialog.update(0, 'Añadiendo episodio...')
    totalepisodes = len(itemlist)
    logger.info ("[launcher.py] Total Episodios:"+str(totalepisodes))
    i = 0
    errores = 0
    nuevos = 0
    for item in itemlist:
        i = i + 1
        pDialog.update(i*100/totalepisodes, 'Añadiendo episodio...',item.title)
        if (pDialog.iscanceled()):
            return

        try:
            #(titulo="",url="",thumbnail="",server="",plot="",canal="",category="Cine",Serie="",verbose=True,accion="strm",pedirnombre=True):
            # Añade todos menos el último (el que dice "Añadir esta serie...")
            if i<len(itemlist):
                nuevos = nuevos + library.savelibrary( titulo=item.title , url=item.url , thumbnail=item.thumbnail , server=item.server , plot=item.plot , canal=item.channel , category="Series" , Serie=item.show.strip() , verbose=False, accion="play_from_library", pedirnombre=False, subtitle=item.subtitle )
        except IOError:
            import sys
            for line in sys.exc_info():
                logger.error( "%s" % line )
            logger.info("[launcher.py]Error al grabar el archivo "+item.title)
            errores = errores + 1
        
    pDialog.close()