import requests
import time

def get_between(original, init_str, end_str, iteration=None):
    if not iteration:
        iteration = 1
    for i in range(iteration):
        original = original[original.find(init_str)+len(init_str):]
        end = original.find(end_str)
        to_ret = original[:end]
        original = original[end:]
    return to_ret


#URL
#http://streamcloud.eu/gd9udz6gfvos
#Fase 1
"""
<form action="" method="POST" class="proform">
                    
                        <input style="text-align: center; font-style: normal; color: #3a3a3a;" type="text" id="countdown" value="Waiting time ? seconds" class="text_field"/>

                        <div class="clear"></div>
                        <br />

                        <input type="hidden" name="op" value="download1">
                        <input type="hidden" name="usr_login" value="">
                        <input type="hidden" name="id" value="gd9udz6gfvos">
                        <input type="hidden" name="fname" value="Los_juegos_del_hambre_En_llamas__TS-Screener___EliteTorrent.net_.avi">
                        <input type="hidden" name="referer" value="http://series.ly/pelis/peli-63XSYD36V7">
                        <input type="hidden" name="hash" value="">
                        <input type="submit" name="imhuman" id="btn_download" class="button gray" value="Watch video now">
                    </form>
"""

def coger(id):
    #URL CORRECTA
    # http://d4444.vidspot.net/d/ycmh2o7oyq5dh6ln5hgy3numfwgxglbf2vlyo4osyn7k42gqwhpxawaq4bvlsxq/video.mp4?v2
    session = requests.Session()

    url_original = 'http://streamcloud.eu/%s' % id
    response = session.get(url=url_original)
    text = response.text

    _id = get_between(original=text,
                         init_str='<input type="hidden" name="id" value="',
                         end_str='">')
    fname = get_between(original=text,
                         init_str='<input type="hidden" name="fname" value="',
                         end_str='">')

    data = {
        'op' : 'download1',
        'usr_login' : '',
        'id': _id,
        'fname' : fname,
        'referer' :'',
        'hash':'',
        'imhuman': 'Watch+video+now',
    }

    time.sleep(10)
    response = session.post(url=url_original, data=data)#headers=headers, data=data)
    text = response.text
    #print text
    to_ret = get_between(original=text,
                         init_str='file: "',
                         end_str='",',
                         iteration=1)
    #print '*'*80
    return to_ret

#Fase2  
#file: "http://cdn1.streamcloud.eu:8080/7tv75bksa6oax3ptx2zipaxe7ssifg5qximi7z4ljgdgahp5f7ta3ppvme/video.mp4",

def get_video_by_id(id):
    return coger(id)

def get_video_by_url(url):
    #Get the id
    id = url.split('/')[-1]
    return get_video_by_id(id)

def main():
    print get_video_by_url('http://streamcloud.eu/gd9udz6gfvos')

if __name__ == '__main__':
    main()