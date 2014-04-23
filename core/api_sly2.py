# -*- coding: iso-8859-15 -*-
import requests
import pickle
import time
import json
import os
#from BeautifulSoup import BeautifulSoup

#Constant
SERIE = 1
MOVIE = 2
DOCU = 3
TVSHOW = 4
EPISODE = 5
SEASON = 6
USER = 7
SUBCOMMENT = 8
LISTA = 9
WEBSERIE = 10
NOTICIA = 11

STATUS = {
    1: 'Favorite',
    2: 'Pending',
    3: 'Viewed',
}

LANGUAGES = {
    'Catalán':1,
    'Castellano': 2,
    'Latino': 3,
    'Euskera': 4,
    'Gallego': 5,
    'Inglés': 6,
    'VO': 7,
    'Sin audio': 8,
}


def get_betweeen(original, init_str, end_str, iteration=None):
    if not iteration:
        iteration = 1
    for i in range(iteration):
        original = original[original.find(init_str)+len(init_str):]
        end = original.find(end_str)
        to_ret = original[:end]
        original = original[end:]
    return to_ret

class APISLY(object):
    def __init__(self, username, password, force=None):
        self.username = username
        self.password = password
        self.session_filename = 'session.dmp'
        self.session = None
        if not force:
            self.force = False
        else:
            self.force = True

        self.login()

    def dump_session(self):
        fd = open(self.session_filename, 'wb')
        pickle.dump(self.session, fd)
        fd.close()

    def load_session(self):
        try:
            fd = open(self.session_filename, 'rb')
            self.session = pickle.load(fd)
            fd.close()
        except:
            return None
        #Check cookie expiration
        cookies = self.session.__getstate__()['cookies']
        for cookie in cookies:
            if cookie.name == 'sess_seriesly2':
                expire_time = int(cookie.expires)
        if expire_time < time.time() - 600:
            return None
        return self.session
        

    def login(self):
        """
        Return login session
        """
        self.session = self.load_session()
        notifications = self.get_notifications()
        if not self.session or self.force or not notifications:
            self.session = requests.Session()
            response = self.session.post(url='http://www.series.ly/scripts/login/login.php', params={
                'lg_login':self.username,
                'lg_pass':self.password,
                'recordar':1,
                })
            if not self.force: #TODO no funciona en XBMC de raspy
                self.dump_session()

    def logout(self):
        try:
            self.session.get(url='http://series.ly/scripts/login/logout.php')
            os.remove('session.dmp')
        except:
            pass

    def _denormalize_status(self, mediaType, status):

        if mediaType == SERIE or mediaType == TVSHOW:
            return status #Sigue este patron
        else:
            try:
                status = int(status)
            except:
                status = None
            if status == 1:
                return 2 #Favorita
            elif status == 2:
                return 3 #Pendiente
            elif status == 3:
                return 1 #Vista

    def _normalize_status(self, mediaType, status):
        """
        Vamos a seguir el patron de:
        - 1 Favorita
        - 2 Pendiente
        - 3 Vista
        """
        if mediaType == SERIE or mediaType == TVSHOW:
            pass #Sigue este patron
        else:
            if status == 1: 
                return 3 #'Viewed'
            elif status == 2: 
                return 1 #'Favorite'
            elif status == 3:
                return 2 #Pending
        return None


    def media_status(self, status, mediaType=None):
        """
        Vista
        Pendiente
        Favorita
        """
        return STATUS[int(status)]

        lang_status1 = 'Favorite'
        lang_status2 = 'Pending'
        lang_status3 = 'Viewed'

        if status == 1:
            return lang_status1
        if status == 2:
            return lang_status2
        if status == 3:
            return lang_status3

    def my_series(self):
        """
        Obtiene un listado de mis series marcadas
        """
        response = self.session.get(url='http://www.series.ly/my-series/')
        #var mediaList = [{"id":"2V675K5Y2R","id2":589,"mN":"The Big Bang Theory","nS":7,"nE":169,"mT":1}];
        #nS es el status
        text = response.text
        """
        start_string = 'var mediaList = [{'
        end_string = '}];'
        start = text.find(start_string)
        text = text[start+len('var mediaList = '):]
        end = text.find(end_string)
        text = text[:end+len(end_string)-1]
        text = json.loads(text)
        """
        series = get_betweeen(original=text, init_str='var mediaList = ',
                                              end_str=';')
        series = json.loads(series)
        media_info = get_betweeen(original=text, init_str='$myMedia = ',
                                  end_str=';')
        media_info = json.loads(media_info)
        media_info_dict = dict()
        for info in media_info:
            media_info_dict[info['idm']] = info
        image_pattern = 'http://cdn.opensly.com/series/%s.jpg'

        to_ret = list()
        for serie in series:
            #print "MOVIE: %s" % repr(movie)
            id2 = serie['id2']
            try:
                serie.update(media_info_dict[id2])
            except:
                pass

            serie['name'] = serie['mN']
            del serie['mN']
            serie['mediaType'] = serie['mT']
            del serie['mT']
            serie['status'] = self._normalize_status(
                                                  mediaType=serie['mediaType'], 
                                                  status=serie['mS'])
            del serie['mS']
            serie['image'] = image_pattern % serie['id']
            to_ret.append(serie)
        
        return to_ret

        #return text

    def change_status(self, idm, mediaType, newStatus):
        
        #Testing
        """
        newStatus 2
        mediaType = 2
        idm = 19647
        """
        #newstatus denormalize 
        #Pelicula, favorita, newStatus 2
        #Pelicula, vista, newStatus 1
        #Pelicula, Pendiente, newStatus 3

        #changeStatusMediaThumbs('12071', 1, mediaType)
        params = {'idm':idm,
                  'newStatus':self._denormalize_status(mediaType=mediaType,
                                                       status=newStatus),
                  'mediaType':mediaType}

        url = "http://series.ly/scripts/media/changeStatus.php"

        self.session.post(url=url,
                          data=params)

    def my_movies(self):
        """
        Obtiene mis peliculas
        TODO
        """
        response = self.session.get(url='http://www.series.ly/my-movies/')
        #var mediaList = [{"id":"2V675K5Y2R","id2":589,"mN":"The Big Bang Theory","nS":7,"nE":169,"mT":1}];
        #nS es el status
        text = response.text
        
        """
        start_string = 'var mediaList = [{'
        end_string = '}];'
        start = text.find(start_string)
        text = text[start+len('var mediaList = '):]
        end = text.find(end_string)
        text = text[:end+len(end_string)-1]
        movies1 = json.loads(text)
        """
        movies = get_betweeen(original=text, init_str='var mediaList = ',
                                              end_str=';')
        movies = json.loads(movies)
        media_info = get_betweeen(original=text, init_str='$myMedia = ',
                                  end_str=';')
        media_info = json.loads(media_info)
        media_info_dict = dict()
        for info in media_info:
            media_info_dict[info['idm']] = info
        
        #thumbURL='http://cdn.opensly.com/'+urlfoto+'/'+id+'.jpg';
        #urlfoto = 
        """
        if(mediaType==SERIE) {
            var link='/series/serie-'+ids;
            var urlfoto='series';
            var media='serie';
        } else if(mediaType==MOVIE){
            var link='/pelis/peli-'+ids;
            var urlfoto='pelis';
            var media='peli';
        }else if(mediaType==DOCU){
            var link='/docus/docu-'+ids;
            var urlfoto='pelis';
            var media='docu';
        }else if(mediaType==TVSHOW){
            var link='/tvshows/show-'+ids;
            var urlfoto='series';
            var media='tvshow';
        """
        #id es la 6HG7SD765
        image_pattern = 'http://cdn.opensly.com/pelis/%s.jpg'
        to_ret = list()
        for movie in movies:
            #print "MOVIE: %s" % repr(movie)
            id2 = movie['id2']
            try:
                movie.update(media_info_dict[id2])
            except:
                pass

            movie['name'] = movie['mN']
            del movie['mN']
            movie['mediaType'] = movie['mT']
            del movie['mT']
            movie['status'] = self._normalize_status(
                                                mediaType=movie['mediaType'], 
                                                status=movie['mS'])
            del movie['mS']
            movie['image'] = image_pattern % movie['id']
            to_ret.append(movie)
        
        #mS es el status
        return to_ret

    def get_serie_info(self, mediaType, id_media):
        """
        Obtiene informacion de una serie concreta
        """
        #id_media = 2V675K5Y2R
        timestamp = int(time.time())
        response = self.session.get(url='http://series.ly/scripts/media/mediaInfo.php',
            params = {'mediaType': mediaType,
                      'id_media': id_media,
                      'v': timestamp})
        to_ret = response.json()

        #view-source:http://series.ly/series/serie-7HV4DXUHE5
        url = 'http://series.ly/series/serie-%s' % id_media
        response = self.session.get(url=url)
        ep_viewed = get_betweeen(original=response.text, 
                                 init_str='var myEpViewed = \'', 
                                 end_str='\';')
        ep_viewed = json.loads(ep_viewed)
        #print ep_viewed
        #TODO Episodios vistos:
        for number, episodes in to_ret['episodes'].iteritems():
            counter = 0
            for episode in episodes:
                if ep_viewed.has_key(str(episode['idc'])):
                    new_episode = episode
                    #print "ENTRA"
                    new_episode['viewed'] = True
                    to_ret['episodes'][number][counter] = new_episode
                counter += 1

        #print ep_viewed
        #print ('*'*80)
        #var myEpViewed = '{"138606":true,"26584":true,"26585":true,"26586":true,"26588":true,"26601":true,"26604":true,"26605":true,"26624":true,"26625":true,"26626":true,"368524":true,"4280":true,"4281":true,"4282":true,"4283":true,"4528":true,"589":true}';

        return to_ret
        
    #Buscar
    def search(self, search_term):
        """
        Buscar por terminos
        """
        response = self.session.get(url='http://series.ly/scripts/search/search.php',
              params= {'s': search_term})

        text = response.text
        start_string = 'slySearch.init({"data":'
        end_string = ',"limit":25,"page":0});'
        start = text.find(start_string)
        text = text[start+len(start_string):]
        end = text.find(end_string)
        text = text[:end+len(end_string)]
        last_sign = text.rfind(']')
        text = text[:last_sign+1]
        json_content = json.loads(text)
        return json_content



    def get_film_details(self, id_media, mediaType):
        """
        Obtiene los detalles de una pelicula
        """
        #id_media is 9WAS7NEHUX
        #mediaType is 2

        timestamp = int(time.time())
        response = self.session.get(
                    url = 'http://www.series.ly/scripts/media/mediaInfo.php',
                    params = {'mediaType': mediaType,
                              'id_media': id_media,
                              'v': timestamp})
        return response.json()

    def get_links(self, idm, mediaType):
        """
        Obtiene el listado de enlaces de un episodio o una pelicula
        """
        try:
            mediaType = int(mediaType)
        except:
            return "mediaType must be integer"
        if mediaType == SERIE or mediaType == TVSHOW:
            mediaType = 5

        timestamp = int(time.time())
        url = 'http://www.series.ly/scripts/media/epLinks.php'
        params = {'mediaType' : mediaType,
                  'idc': idm,
                  'time' : '%d.txt' % timestamp }

        response = self.session.get(url=url,
                                    params=params)
        return response.json()

    def get_video_link(self, idv, mediaType): #Youtube link or similar
        """
        Obtiene el enlace del player
        """
        try:
            mediaType = int(mediaType)
        except:
            return "mediaType must be integer"
        if mediaType == SERIE or mediaType == TVSHOW:
            mediaType = 5
        response = self.session.get(
                            url='http://series.ly/scripts/media/gotoLink.php',
                            params= {'idv': idv, 'mediaType' : mediaType})

        return response.url

    def get_notifications(self):
        """
        Mira las notificaciones
        """
        try:
            url_query = 'http://www.series.ly/scripts/notifications/get.php'
            response = self.session.get(url=url_query)
            return response.json()
        except:
            return None

    def get_activity(self):
        params = {'type':'connections',
                   'limit':6}
        response =self.session.get(
                     url='http://series.ly/scripts/activity/activitylist.php',
                     params=params)
        return response.json()

    def _parse_catalogue(self, content):
        pass

    def get_most_valuated_series(self):
        pass
        #http://series.ly/scripts/catalogue/index.php?page=0&mediaType=1

    def get_most_valuated_films(self):
        pass
        #http://series.ly/scripts/catalogue/index.php?page=0&mediaType=2


    def report_video(self, ids, idv, idc, mediaType, errorType, election):
        pass
        #Idioma incorrecto, esta en VO
        # POST http://series.ly/scripts/media/report.php
        #DATA:
        #DAtos episodio
        params = {
            'election': election,
            'errorType': errorType,
            'idm': ids,
            'idv': '??',
            'mediaType': mediaType,
            'episodeIdm': idc,
        }
        """
        {
            u'mediaType_media': 1,
            u'episode': 18,
            u'name': u'Lavariantedelospantalones',
            u'title': u'Lavariantedelospantalones',
            u'season': 3,
            u'mediaType': u'1',
            u'ids': 589,
            u'idm_media': 589,
            u'title_es': u'Lavariantedelospantalones',
            u'num': 18,
            u'haveLinks': True,
            'viewed': True,
            u'timestamp': 1392687195,
            u'idc': 52103,
            u'has_links': True
        }
        """
        #'idv': '5122208', 'mediaType': '1', 'host': 'Vidspot', 'idm': '52103',
        #Datos Necesarios
        #mediaType -> OK
        #idm -> OK (es el ids del episodio) -> Corregido
        #idv -> OK (Es el idv del enlace)
        #episodeIdm -> (OK, es el idc)
        #Datos enviados
        """
        election:7
        errorType:language
        idm:589
        idv:5122208
        mediaType:1
        episodeIdm:52103
        """
        """
        Elections in language
            <option value="1">Català</option>
            <option value="2">Castellano</option>
            <option value="3">Latino</option>
            <option value="4">Euskera</option>
            <option value="5">Gallego</option>
            <option value="6">Inglés</option>
            <option value="7">VO</option>
            <option value="8">Sin audio</option>
        """
"""
def get_catalog(self):
    
    Obtiene el catalogo
    TODO
    
    url = 'http://www.series.ly/scripts/catalogue/'
    response = self.session.get(url=url)
    soup = BeautifulSoup(response.text)
    anchors = soup.findAll('a', {'class':'ajaxSend'})
    #anchors = soup.findChildren('a', {'class':'ajaxSend'})
    anchors = anchors[8:-5]
    for anchor in anchors:
        print anchor
        #TODO
        
        #children = anchor.findChildren()
        #for child in children:
        #    print child
        
        #print anchor
"""

def main():
    import settings
    api = APISLY(username=settings.get_config('login', 'username'), 
                 password=settings.get_config('login', 'password'), 
                 force=True)
    #print get_notifications(ses)
    #get_catalog(ses)
    print api.get_serie_info(mediaType='1', id_media='7HV4DXUHE5')
if __name__ == '__main__':
    main()
    #print api.my_series()