'''
   YouTube plugin for XBMC
    Copyright (C) 2010-2012 Tobias Ussing And Henrik Mosgaard Jensen

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import urllib
import os
import cgi
from core import logger
import xbmcgui
import xbmcplugin
import xbmc
try: import simplejson as json
except ImportError: import json

import urllib2
import xbmcaddon


import CommonFunctions as common
common.plugin = 'seriesly'

settings = xbmcaddon.Addon(id='plugin.video.seriesly')

class SettingMIO(object):
    def __init__(self):
        self.settings = dict()
        self.settings['lang_code'] = 0
        self.settings['annotations'] = 'false'
        self.settings['hd_videos_download'] = True
        self.settings['hd_videos'] = 3

    def getSetting(self, key):
        if self.settings.has_key(key):
            return self.settings[key]


APIKEY = "AI39si6hWF7uOkKh4B9OEAX-gK337xbwR9Vax-cdeF9CF9iNAcQftT8NVhEXaORRLHAmHxj6GjM-Prw04odK4FxACFfKkiH9lg"

class url2request(urllib2.Request):
    """Workaround for using DELETE with urllib2"""
    def __init__(self, url, method, data=None, headers={}, origin_req_host=None, unverifiable=False):
        self._method = method
        urllib2.Request.__init__(self, url, data, headers, origin_req_host, unverifiable)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self)

class Player():
    fmt_value = {
        5: "240p h263 flv container",
        18: "360p h264 mp4 container | 270 for rtmpe?",
        22: "720p h264 mp4 container",
        26: "???",
        33: "???",
        34: "360p h264 flv container",
        35: "480p h264 flv container",
        37: "1080p h264 mp4 container",
        38: "720p vp8 webm container",
        43: "360p h264 flv container",
        44: "480p vp8 webm container",
        45: "720p vp8 webm container",
        46: "520p vp8 webm stereo",
        59: "480 for rtmpe",
        78: "seems to be around 400 for rtmpe",
        82: "360p h264 stereo",
        83: "240p h264 stereo",
        84: "720p h264 stereo",
        85: "520p h264 stereo",
        100: "360p vp8 webm stereo",
        101: "480p vp8 webm stereo",
        102: "720p vp8 webm stereo",
        120: "hd720",
        121: "hd1080"
        }

    # YouTube Playback Feeds
    urls = {}
    urls['video_stream'] = "http://www.youtube.com/watch?v=%s&safeSearch=none"
    urls['embed_stream'] = "http://www.youtube.com/get_video_info?video_id=%s"
    urls['video_info'] = "http://gdata.youtube.com/feeds/api/videos/%s"

    def __init__(self):
        
        self.settings = SettingMIO() #sys.modules["__main__"].settings
        
        self.dbg=True

    def showErrorMessage(self, title="", result="", status=500):
        if title == "":
            title = 'Error'
        if result == "":
            result = "Error desconocido"

        if (status == 303):
            self.showMessage(title, result)
            logger.error(result)
        else:
            self.showMessage(title, "Error desconocido")
            logger.error(result)


    def showMessage(self, heading, message):
        logger.debug(repr(type(heading)) + " - " + repr(type(message)))
        duration = ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10][int(5)]) * 1000
        xbmc.executebuiltin((u'XBMC.Notification("%s", "%s", %s)' % (heading, message, duration)).encode("utf-8"))

    def addSubtitles(self, video={}):
        get = video.get
        logger.debug(u"fetching subtitle if available")

        filename = 'a'#self.getSubtitleFileName(video)
        filename = ""
        download_path = os.path.join('~/.xbmc/temp/', filename)
        path = os.path.join(xbmc.translatePath(settings.getAddonInfo("profile")).decode("utf-8"), filename)

        set_subtitle = False
        """
        if self.xbmcvfs.exists(download_path):
            path = download_path
            set_subtitle = True
        elif self.xbmcvfs.exists(path):
            set_subtitle = True
        elif self.downloadSubtitle(video):
            set_subtitle = True
        """
        logger.debug(u"Done trying to locate: " + path)

        if os.path.exists(path) and not "download_path" in video and set_subtitle:
            player = xbmc.Player()

            i = 0
            while not player.isPlaying():
                i += 1
                logger.debug(u"Waiting for playback to start ")
                time.sleep(1)
                if i > 10:
                    break

            xbmc.Player().setSubtitles(path)
            logger.debug(u"added subtitle %s to playback" % path)


    def playVideo(self, params={}):
        logger.debug("ENTRAAAAAAAA")

        #params = {'action': 'play_video', 'path': '/root/video', 'videoid': 'klFX6grYwGE'}
        logger.debug("PLAYVIDEO_PARAMS: %s" % repr(params))
        get = params.get

        (video, status) = self.buildVideoObject(params)

        if status != 200:
            logger.debug(u"construct video url failed contents of video item " + repr(video))
            self.showErrorMessage("Reproduccion de lista abortada", video["apierror"], status)
            return False
        #video['video_url'] = 'http://r7---sn-w511uxa-h5qs.googlevideo.com/videoplayback?expire=1389677298&fexp=905024,916807,914071,916624,924616,938630,936910,936913,907231,907240,921090&id=4c7795bb790afd97&ms=au&ipbits=0&mv=m&source=youtube&sparams=id,ip,ipbits,itag,ratebypass,source,upn,expire&itag=22&ratebypass=yes&upn=hvLibnHF2xY&ip=188.76.234.250&key=yt5&mt=1389653896&sver=3&signature=B1E6E782D863C1986A240FEC0BA6EE7810C34FFE.B11DA9E4D9FFDE60CF255AF95434DF6DB6B4E458|User-Agent=Mozilla%2F5.0+%28Windows+NT+6.2%3B+Win64%3B+x64%3B+rv%3A16.0.1%29+Gecko%2F20121011+Firefox%2F16.0.1'
        #video['video_url'] = 'http://r6---sn-w511uxa-h5qe.googlevideo.com/videoplayback?key=yt5&itag=22&source=youtube&sparams=id,ip,ipbits,itag,ratebypass,source,upn,expire&expire=1389684908&ratebypass=yes&ipbits=0&ms=au&fexp=933208,938630,936910,936913,907231,907240,921090&sver=3&ip=188.76.234.250&mt=1389661203&id=b663572aa794b493&mv=m&upn=26YgOV1ykH8&signature=9B0F4CC58A800E59333AB2E8430FC11DF6BD6C30.DC4E161A7D44A1603DAA1B447DC419BFC05FC17F|User-Agent=Mozilla%2F5.'
        #return 'http://r5---sn-w511uxa-h5qs.googlevideo.com/videoplayback?ip=188.76.234.250&sver=3&fexp=903708,901802,910100,916625,938630,936910,936913,907231,907240,921090&sparams=id,ip,ipbits,itag,ratebypass,source,upn,expire&upn=zeHQHxzAbPQ&itag=43&ipbits=0&ms=au&mv=m&id=e780fda3705ce1d3&expire=1389780002&source=youtube&ratebypass=yes&key=yt5&mt=1389755688&signature=78275591E1E2A860F7454E40854C90035B8FAEFFF1738F226496D83A421FD31B3799F72F96F9D769|User-Agent=Mozilla%2F5.0+%28Windows+NT+6.2%3B+Win64%3B+x64%3B+rv%3A16.0.1%29+Gecko%2F20121011+Firefox%2F16.0.1'
        #return 'http://r8---sn-w511uxa-h5ql.googlevideo.com/videoplayback?ratebypass=yes&ipbits=0&expire=1389776594&fexp=934702,924614,930103,916615,924616,938630,936910,936913,907231,907240,921090&mt=1389753857&ip=188.76.234.250&key=yt5&source=youtube&ms=au&upn=wWWvlnXimYo&sver=3&mv=m&id=46337c79ae62c8ec&sparams=id,ip,ipbits,itag,ratebypass,source,upn,expire&itag=22&signature=45457BDE01E203BD1990512859180B054E4C8B8D.8C4F098ABBB93C004159A69191E5896B9316760B|User-Agent=Mozilla%2F5.0+%28Windows+NT+6.2%3B+Win64%3B+x64%3B+rv%3A16.0.1%29+Gecko%2F20121011+Firefox%2F16.0.1'
        #return 'http://85.12.5.196:8777/capymvjiesie2cbd4ph3xdncaugaffsubx2kl34wrrtffcqxu3djabubma/v.mp4.flv'
        #return 'http://www.dailymotion.com/swf/video/x11jgfm?wmode=transparent&isInIframe=1&start=0&api=false&id=&network=dsl&startscreen=flash&controls=flash&related=1&reporting=1&logo=0&country=ES&prod=true&preprod=false&instream=false&referer=http%3A%2F%2Fwww.playedto.com%2Fvideos%2Fcaminando-entre-dinosaurios-2013%2F&ip=188.76.234.250&is_partner_player=false&autoplay=0&hideInfos=0&syndication=121412&foreground=&highlight=&background=&gifloader=false&chromeless=0&forcedQuality=sd&enableApi=1&parentURL=http%3A%2F%2Fwww.playedto.com%2Fvideos%2Fcaminando-entre-dinosaurios-2013%2F&metaAutoplay=0&_='
        base = 'http://www.youtube.com/v/9No-FiEInLA?version=3&hl=en_US'
        return base # % params['videoid']
        #logger.debug("URL_YOUTUBE: %s" % video['video_url'])
        #return 'http://www.youtube.com/watch?v=9gJxJw8HWJ8'
        return video['video_url']
        listitem = xbmcgui.ListItem(label=video['Title'], iconImage=video['thumbnail'], thumbnailImage=video['thumbnail'], path=video['video_url'])
        #listitem = xbmcgui.ListItem(label="TITULO", path=video['video_url'])
        logger.debug("VIDEO_PATH %s" % video['video_url'])
        listitem.setInfo(type='Video', infoLabels=video)

        logger.debug(u"Playing video: " + repr(video['Title']) + " - " + repr(get('videoid')) + " - " + repr(video['video_url']))

        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)
        logger.debug("MIO1 %s" % repr(sys.argv[1]))
        logger.debug("MIO1 %s" % repr(listitem))

        if self.settings.getSetting("lang_code") != "0" or self.settings.getSetting("annotations") == "true":
            logger.debug("BLAAAAAAAAAAAAAAAAAAAAAA: " + repr(self.settings.getSetting("lang_code")))
            self.addSubtitles(video) #TODO
        #xbmc.Player()

        #if (get("watch_later") == "true" and get("playlist_entry_id")):
        #    logger.debug(u"removing video from watch later playlist")
        #    #self.core.remove_from_watch_later(params)

        #self.storage.storeValue("vidstatus-" + video['videoid'], "7")

    def getInfo(self, params):
        get = params.get
        video = ''#self.cache.get("videoidcache " + get("videoid"))
        if len(video) > 0:
            logger.debug(u"returning cache ")
            return (eval(video), 200)

        result = fetchPage({"link": self.urls["video_info"] % get("videoid"), "api": "true"})

        if result["status"] == 200:
            video = getVideoInfo(result["content"], params)

            if len(video) == 0:
                logger.debug(u"- Couldn't parse API output, YouTube doesn't seem to know this video id?")
                video = {}
                video["apierror"] = "ERROR2"#self.language(30608)
                return (video, 303)
        else:
            logger.debug(u"- Got API Error from YouTube!")
            video = {}
            video["apierror"] = result["content"]

            return (video, 303)

        video = video[0]
        #self.cache.set("videoidcache" + get("videoid"), repr(video))
        return (video, result["status"])
    
    def selectVideoQuality(self, params, links):
        get = params.get

        print "links: " + repr(type(links).__name__)
        link = links.get
        video_url = ""

        logger.debug(u"")

        if get("action") == "download":
            hd_quality = self.settings.getSetting("hd_videos_download")
            if hd_quality:
                hd_quality = int(self.settings.getSetting("hd_videos"))

        else:
            if (not get("quality")):
                hd_quality = int(self.settings.getSetting("hd_videos"))
            else:
                if (get("quality") == "1080p"):
                    hd_quality = 3
                elif (get("quality") == "720p"):
                    hd_quality = 2
                else:
                    hd_quality = 1

        # SD videos are default, but we go for the highest res
        if (link(35)):
            video_url = link(35)
        elif (link(59)):
            video_url = link(59)
        elif link(44):
            video_url = link(44)
        elif (link(78)):
            video_url = link(78)
        elif (link(34)):
            video_url = link(34)
        elif (link(43)):
            video_url = link(43)
        elif (link(26)):
            video_url = link(26)
        elif (link(18)):
            video_url = link(18)
        elif (link(33)):
            video_url = link(33)
        elif (link(5)):
            video_url = link(5)

        if hd_quality > 1:  # <-- 720p
            if (link(22)):
                video_url = link(22)
            elif (link(45)):
                video_url = link(45)
            elif link(120):
                video_url = link(120)
        if hd_quality > 2:
            if (link(37)):
                video_url = link(37)
            elif link(121):
                video_url = link(121)

        if link(38) and False:
            video_url = link(38)

        for fmt_key in links.iterkeys():
            if link(int(fmt_key)):
                if self.dbg:
                    text = repr(fmt_key) + " - "
                    if fmt_key in self.fmt_value:
                        text += self.fmt_value[fmt_key]
                    else:
                        text += "Unknown"

                    if (link(int(fmt_key)) == video_url):
                        text += "*"
                    logger.debug(text)
            else:
                logger.debug(u"- Missing fmt_value: " + repr(fmt_key))

        if hd_quality == 0 and not get("quality"):
            logger.debug("SELECCIONA CALIDAD DEL VIDEO")
            return self.userSelectsVideoQuality(params, links)

        if not len(video_url) > 0:
            logger.debug(u"- construct_video_url failed, video_url not set")
            return video_url

        if get("action") != "download" and video_url.find("rtmp") == -1:
            video_url += '|' + urllib.urlencode({'User-Agent':common.USERAGENT})

        logger.debug(u"Done")
        return video_url
    
    def userSelectsVideoQuality(self, params, links):
        levels =    [([37,121], u"1080p"),
                     ([22,45,120], u"720p"),
                     ([35,44], u"480p"),
                     ([18], u"380p"),
                     ([34,43],u"360p"),
                     ([5],u"240p"),
                     ([17],u"144p")]

        link = links.get
        quality_list = []
        choices = []

        for qualities, name in levels:
            for quality in qualities:
                if link(quality):
                    quality_list.append((quality, name))
                    break

        for (quality, name) in quality_list:
            choices.append(name)

        dialog = xbmcgui.Dialog()
        selected = dialog.select("Calidad del video", choices) #self.language(30518)

        if selected > -1:
            (quality, name) = quality_list[selected]
            return link(quality)

        return u""
    
    def checkForErrors(self, video):
        status = 200

        if "video_url" not in video or video[u"video_url"] == u"":
            status = 303
            if u"apierror" not in video:
                vget = video.get
                if vget(u"live_play"):
                    video[u'apierror'] = "ERROR3"#self.language(30612)
                    logger.debug("ERROR3")
                elif vget(u"stream_map"):
                    video[u'apierror'] = "ERROR4"#self.language(30620)
                    logger.debug("ERROR4")
                else:
                    video[u'apierror'] = "ERROR5"#self.language(30618)
                    logger.debug("ERROR5")

        return (video, status)

    def buildVideoObject(self, params):
        logger.debug(repr(params))

        (video, status) = self.getInfo(params)

        if status != 200: #USA ESTE CAMINO SI LA API_KEY NO ESTA BIEN
            logger.debug("YOUTUBE: ERROR6")
            video[u'apierror'] = "No se ha podido localizar la url de video"
            return (video, 303)

        video_url = self.getLocalFileSource(params, video)
        if video_url:
            video[u'video_url'] = video_url
            logger.debug("YOUTUBE: OK1")
            return (video, 200)
        logger.debug("YOUTUBE: OTHERWAY 1")
        (links, video) = self.extractVideoLinksFromYoutube(video, params)

        if len(links) != 0:
            video[u"video_url"] = self.selectVideoQuality(params, links)
        elif "hlsvp" in video:
            #hls selects the quality based on available bitrate (adaptive quality), no need to select it here
            video[u"video_url"] = video[u"hlsvp"]
            logger.debug("Using hlsvp url %s" % video[u"video_url"])

        (video, status) = self.checkForErrors(video)

        logger.debug(u"Done")

        return (video, status)


    def getLocalFileSource(self, params, video):
        self.INVALID_CHARS = "\\/:*?\"<>|"
        get = params.get
        result = u""
        if (get("action", "") != "download"):
            path = '~/.xbmc/temp' #self.settings.getSetting("download_path")
            video['Title'] = 'Test title'
            #filename = u"".join(c for c in common.makeUTF8(video['Title']) if c not in self.INVALID_CHARS) + u"-[" + get('videoid') + u"]" + u".mp4"
            filename_list = list()
            for c in common.makeUTF8(video['Title']):
                if c not in self.INVALID_CHARS:
                    filename_list.append(c)
            filename = u''.join(filename_list) + u"-[" + get('videoid') + u"]" + u".mp4"
            path = os.path.join(path.decode("utf-8"), filename)
            try:
                if os.path.exists(path):
                    result = path
            except:
                logger.debug(u"failed to locate local subtitle file, trying youtube instead")
        return result

    def removeAdditionalEndingDelimiter(self, data):
        pos = data.find("};")
        if pos != -1:
            logger.debug(u"found extra delimiter, removing")
            data = data[:pos + 1]
        return data

    def extractFlashVars(self, data):
        flashvars = {}
        found = False

        for line in data.split("\n"):
            if line.strip().find(";ytplayer.config = ") > 0:
                found = True
                p1 = line.find(";ytplayer.config = ") + len(";ytplayer.config = ") - 1
                p2 = line.rfind(";")
                if p1 <= 0 or p2 <= 0:
                    continue
                data = line[p1 + 1:p2]
                break
        data = self.removeAdditionalEndingDelimiter(data)

        if found:
            data = json.loads(data)
            flashvars = data["args"]
        logger.debug("Step2: " + repr(data))

        logger.debug(u"flashvars: " + repr(flashvars))
        return flashvars

    def scrapeWebPageForVideoLinks(self, result, video):
        logger.debug(u"")
        links = {}

        flashvars = self.extractFlashVars(result[u"content"])
        if not flashvars.has_key(u"url_encoded_fmt_stream_map"):
            return links

        if flashvars.has_key(u"ttsurl"):
            video[u"ttsurl"] = flashvars[u"ttsurl"]

        if flashvars.has_key(u"hlsvp"):                               
            video[u"hlsvp"] = flashvars[u"hlsvp"]    

        for url_desc in flashvars[u"url_encoded_fmt_stream_map"].split(u","):
            url_desc_map = cgi.parse_qs(url_desc)
            logger.debug(u"url_map: " + repr(url_desc_map))
            if not (url_desc_map.has_key(u"url") or url_desc_map.has_key(u"stream")):
                continue

            key = int(url_desc_map[u"itag"][0])
            url = u""
            if url_desc_map.has_key(u"url"):
                url = urllib.unquote(url_desc_map[u"url"][0])
            elif url_desc_map.has_key(u"conn") and url_desc_map.has_key(u"stream"):
                url = urllib.unquote(url_desc_map[u"conn"][0])
                if url.rfind("/") < len(url) -1:
                    url = url + "/"
                url = url + urllib.unquote(url_desc_map[u"stream"][0])
            elif url_desc_map.has_key(u"stream") and not url_desc_map.has_key(u"conn"):
                url = urllib.unquote(url_desc_map[u"stream"][0])

            if url_desc_map.has_key(u"sig"):
                url = url + u"&signature=" + url_desc_map[u"sig"][0]
            elif url_desc_map.has_key(u"s"):
                sig = url_desc_map[u"s"][0]
                url = url + u"&signature=" + self.decrypt_signature(sig)

            links[key] = url

        return links

    def decrypt_signature(self, s):
        ''' use decryption solution by Youtube-DL project '''
        if len(s) == 88:
            return s[48] + s[81:67:-1] + s[82] + s[66:62:-1] + s[85] + s[61:48:-1] + s[67] + s[47:12:-1] + s[3] + s[11:3:-1] + s[2] + s[12]
        elif len(s) == 87:
            return s[62] + s[82:62:-1] + s[83] + s[61:52:-1] + s[0] + s[51:2:-1]
        elif len(s) == 86:
            return s[2:63] + s[82] + s[64:82] + s[63]
        elif len(s) == 85:
            return s[76] + s[82:76:-1] + s[83] + s[75:60:-1] + s[0] + s[59:50:-1] + s[1] + s[49:2:-1]
        elif len(s) == 84:
            return s[83:36:-1] + s[2] + s[35:26:-1] + s[3] + s[25:3:-1] + s[26]
        elif len(s) == 83:
            return s[6] + s[3:6] + s[33] + s[7:24] + s[0] + s[25:33] + s[53] + s[34:53] + s[24] + s[54:]
        elif len(s) == 82:
            return s[36] + s[79:67:-1] + s[81] + s[66:40:-1] + s[33] + s[39:36:-1] + s[40] + s[35] + s[0] + s[67] + s[32:0:-1] + s[34]
        elif len(s) == 81:
            return s[6] + s[3:6] + s[33] + s[7:24] + s[0] + s[25:33] + s[2] + s[34:53] + s[24] + s[54:81]
        elif len(s) == 92:
            return s[25] + s[3:25] + s[0] + s[26:42] + s[79] + s[43:79] + s[91] + s[80:83];
        else:
            logger.debug(u'Unable to decrypt signature, key length %d not supported; retrying might work' % (len(s)))

    def getVideoPageFromYoutube(self, get):
        login = "false"

        #if self.pluginsettings.userHasProvidedValidCredentials():
        #    login = "true"

        page = fetchPage({u"link": self.urls[u"video_stream"] % get(u"videoid"), "login": login})
        logger.debug("Step1: " + repr(page["content"].find("ytplayer")))

        if not page:
            page = {u"status":303}

        return page

    def isVideoAgeRestricted(self, result):
        error = common.parseDOM(result['content'], "div", attrs={"id": "watch7-player-age-gate-content"})
        logger.debug(repr(error))
        return len(error) > 0

    def extractVideoLinksFromYoutube(self, video, params):
        logger.debug(u"trying website: " + repr(params))
        get = params.get

        result = self.getVideoPageFromYoutube(get)
        if False:#self.isVideoAgeRestricted(result): #Restricciones de edad, me las paso por el arco
            logger.debug(u"Age restricted video")
            if False:#self.pluginsettings.userHasProvidedValidCredentials():
                #self.login._httpLogin({"new":"true"})
                result = self.getVideoPageFromYoutube(get)
            else:
                video[u"apierror"] = "ERROR1"#self.language(30622)

        if result[u"status"] != 200: #No se puede extraer el video de YOUTUBE
            logger.debug(u"Couldn't get video page from YouTube")
            return ({}, video)

        links = self.scrapeWebPageForVideoLinks(result, video)

        if len(links) == 0 and not( "hlsvp" in video ):
            logger.debug(u"Couldn't find video url- or stream-map.")

            if not u"apierror" in video:
                video[u'apierror'] = "AS"#self.core._findErrors(result)

        logger.debug(u"Done")
        return (links, video)



def fetchPage(params={}):  # This does not handle cookie timeout for _httpLogin
    #if self.settings.getSetting("force_proxy") == "true" and self.settings.getSetting("proxy"):
    #    params["proxy"] = self.settings.getSetting("proxy")

    get = params.get
    link = get("link")
    ret_obj = {"status": 500, "content": "", "error": 0}
    cookie = ""

    if (get("url_data") or get("request") or get("hidden")) and False:
        print("called for : " + repr(params['link']))
    else:
        print("called for : " + repr(params))

    if get("auth", "false") == "true":
        print("got auth")
        if False:#self._getAuth():
            if link.find("?") > -1:
                link += "&oauth_token=" + self.settings.getSetting("oauth2_access_token")
            else:
                link += "?oauth_token=" + self.settings.getSetting("oauth2_access_token")

            print("updated link: " + link)
        else:
            print("couldn't get login token")

    if not link or get("error", 0) > 2:
        print("giving up")
        return ret_obj

    if get("url_data"):
        request = urllib2.Request(link, urllib.urlencode(get("url_data")))
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    elif get("request", "false") == "false":
        if get("proxy"):
            proxy = get("proxy")
            link = proxy + urllib.quote(link)
            print("got proxy: %s" % link)
        else:
            print("got default: %s" % link)

        request = url2request(link, get("method", "GET"))
    else:
        print("got request")
        request = urllib2.Request(link, get("request"))
        request.add_header('X-GData-Client', "")
        request.add_header('Content-Type', 'application/atom+xml')
        request.add_header('Content-Length', str(len(get("request"))))

    if False:#get("proxy") or (self.settings.getSetting("proxy") != "" and link.find(self.settings.getSetting("proxy")) > -1):
        proxy = self.settings.getSetting("proxy")
        referer = proxy[:proxy.rfind("/")]
        print("Added proxy refer: %s" % referer)

        request.add_header('Referer', referer)

    if get("api", "false") == "true":
        print("got api")
        request.add_header('GData-Version', '2.1')
        request.add_header('X-GData-Key', 'key=' + APIKEY)
    else:
        request.add_header('User-Agent', common.USERAGENT)

        if get("no-language-cookie", "false") == "false" and False:
            cookie += "PREF=f1=50000000&hl=en; "

    if get("login", "false") == "true":
        print("got login")
        if True:#(self.settings.getSetting("username") == "" or self.settings.getSetting("user_password") == ""):
            print("_fetchPage, login required but no credentials provided")
            ret_obj["status"] = 303
            ret_obj["content"] = self.language(30622)
            return ret_obj

        # This should be a call to self.login._httpLogin()
        if False:#self.settings.getSetting("cookies_saved") != "true":
            if isinstance(self.login, str):
                self.login = sys.modules["__main__"].login
            self.login._httpLogin()

    if get("referer", "false") != "false":
        print("Added referer: %s" % get("referer"))
        request.add_header('Referer', get("referer"))

    try:
        print("connecting to server... %s" % link )

        if cookie:
            print("Setting cookie: " + cookie)

        con = urllib2.urlopen(request)

        inputdata = con.read()
        ret_obj["content"] = inputdata.decode("utf-8")
        ret_obj["location"] = link

        ret_obj["new_url"] = con.geturl()
        ret_obj["header"] = str(con.info())
        con.close()

        print("Result: %s " % repr(ret_obj), 9)

        print("done")
        ret_obj["status"] = 200
        return ret_obj

    except urllib2.HTTPError, e:
        cont = False
        err = str(e)
        msg = e.read()

        print("HTTPError : " + err)
        if e.code == 400 or True:
            print("Unhandled HTTPError : [%s] %s " % (e.code, msg), 1)

        params["error"] = get("error", 0) + 1
        #ret_obj = self._fetchPage(params)

        if cont and ret_obj["content"] == "":
            ret_obj["content"] = cont
            ret_obj["status"] = 303

        return ret_obj

    except urllib2.URLError, e:
        err = str(e)
        print("URLError : " + err)
        if err.find("SSL") > -1:
            ret_obj["status"] = 303
            #ret_obj["content"] = self.language(30629)
            ret_obj["error"] = 3  # Tell _findErrors that we have an error
            return ret_obj

        time.sleep(3)
        params["error"] = get("error", 0) + 1
        #ret_obj = self._fetchPage(params)
        return ret_obj

    except socket.timeout:
        print("Socket timeout")
        return ret_obj



def getVideoEntries(xml):
    entries = common.parseDOM(xml, "entry")
    if not entries:
        entries = common.parseDOM(xml, "atom:entry")

    return entries

def getVideoId(node):
    videoid = "false"
    for id in common.parseDOM(node, "yt:videoid"):
        videoid = id

    if videoid == "false":
        for id in common.parseDOM(node, "content", ret="src"):
            videoid = id
            videoid = videoid[videoid.rfind("/") + 1:]

    if videoid == "false":
        for id in common.parseDOM(node, "link", ret="href"):
            match = re.match('.*?v=(.*)\&.*', id)
            if match:
                videoid = match.group(1)

    return videoid

def getVideoInfo(xml, params={}):
    
    entries = getVideoEntries(xml)

    ytobjects = []
    for node in entries:
        video ={}

        video["videoid"] = getVideoId(node)
        #video["playlist_entry_id"] = self.getPlaylistId(node)
        #video['editid'] = self.getVideoEditId(node)

        if False:#self.videoIsUnavailable(node):
            self.common.log("Video is unavailable, removing from result.", 3)
            video["videoid"] = "false"

        #video["Studio"] = self.getVideoCreator(node)
        #video["Title"] = self.getVideoTitle(node)
        #video["Duration"] = self.getVideoDuration(node)
        #video["Rating"] = self.getVideoRating(node)
        #video["Genre"] = self.getVideoGenre(node)

        #viewCount = self.getViewCount(node)
        #video["Count"] = viewCount
        #uploadDate = self.getVideoUploadDate(node)
        #video['Date'] = time.strftime("%d-%m-%Y", uploadDate)

        #video["Plot"] = self.getVideoDescription(node, uploadDate, viewCount)
        urls_thumbs = "http://i.ytimg.com/vi/%s/0.jpg"
        video['thumbnail'] = urls_thumbs % video['videoid']

        ytobjects.append(video)

    #self.addNextPageLinkIfNecessary(params, xml, ytobjects)

    #self.updateVideoIdStatusInCache("videoidcache", ytobjects)
    #self.getVideoIdStatusFromCache("vidstatus-", ytobjects)

    #self.common.log("Done: " + str(len(ytobjects)),3)
    return ytobjects