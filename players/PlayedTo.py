import requests
import Cookie
import time

def coger(session, id):
    headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0'}
    
    response = session.get(url='http://played.to/%s' % id, headers=headers)
    
    text = response.text

    """
    COOKIES
    $.cookie('file_id', '818883', { expires: 10 });
    $.cookie('aff', '1', { expires: 10 });
    """
    #cookie = {'enwiki_session': '17ab96bd8ffbe8ca58a78657a918558'}

    #r = requests.post('http://wikipedia.org', cookies=cookie)
    cookies = dict()

    cookie1_text = '$.cookie(\'file_id\', \''
    cookie1_value = text[text.find(cookie1_text)+len(cookie1_text):]
    end = cookie1_value.find('\', { expires')
    cookie1_value = cookie1_value[:end]
    #print "COOKIE1: %s" % cookie1_value

    cookie2_text = '$.cookie(\'aff\', \''
    cookie2_value = text[text.find(cookie2_text)+len(cookie2_text):]
    end = cookie2_value.find('\', { expires')
    cookie2_value = cookie2_value[:end]
    #print "COOKIE2: %s" % cookie2_value

    
    cookies['file_id'] = str(cookie1_value)
    cookies['aff'] = str(cookie2_value)
    #cookies['lang'] = 'spanish'

    """
    <input type="hidden" name="op" value="download1">
    <input type="hidden" name="usr_login" value="">
    <input type="hidden" name="id" value="keyd8tqkmep0">

    <input type="hidden" name="fname" value="CARTOONSRUDOLPHTHERE.mp4.flv">
    <input type="hidden" name="referer" value="">
    <input type="hidden" name="hash" value="47ulr4zgbqgw44u7sskxyzkd4bvkph3h">
    <input type="submit" name="imhuman" value="Continue to Video" id="btn_download" disabled="disabled">

    """
    '<input type="hidden" name="id" value="'
    text_id_form = '<input type="hidden" name="id" value="'
    id_form = text[text.find(text_id_form)+len(text_id_form):]
    end = id_form.find('">')
    id_form = id_form[:end]
    #print "ID_FORM: %s" % id_form

    text_fname = '<input type="hidden" name="fname" value="'
    fname = text[text.find(text_fname)+len(text_fname):]
    end = fname.find('">')
    fname = fname[:end]
    #print "FNAME: %s" % fname

    text_hash = '<input type="hidden" name="hash" value="'
    _hash = text[text.find(text_hash)+len(text_hash):]
    end = _hash.find('">')
    _hash = _hash[:end]
    #print "HASH: %s" % _hash

    return (id_form, fname, _hash, cookies)

def coger2(session, cookies, id, fname, hash):
    params = {'op': 'download1',
              'usr_login': '',
              'id': id,
              'fname': fname,
              'referer': '',
              'hash': hash,
              'imhuman': 'Continue to Video',
              }
    headers = {#'Referer':'http://played.to/%s' % id,
                'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0',
                }
    response = session.post(url='http://played.to/%s' % id, 
                            data=params,
                            headers=headers, 
                            cookies=cookies
                            )
    text = response.text
    #print response.headers
    #print response.text
    #print params
    init_text = 'file: "'
    end_text = '",'
    init = text[text.find(init_text)+len(init_text):]
    #end = fname.find('">')
    #fname = fname[:end]
    source = init[:init.find(end_text)]
    return source
    #coo = response.cookies
    #for c in coo:
    #    print c
    #print cookies
    #print response.history#[0].url

def get_video_by_id(id):
    session = requests.Session()
    (_id, fname, _hash, cookies) = coger(session, id)
    
    return coger2(session, cookies, _id, fname, _hash)

def get_video_by_url(url):
    #Get the id
    id = url.split('/')[-1]
    return get_video_by_id(id)

def main():
    session = requests.Session()
    (_id, fname, _hash, cookies) = coger(session, 'onhde0fawvyv')
    
    print coger2(session, cookies, _id, fname, _hash)

if __name__ == '__main__':
    main()