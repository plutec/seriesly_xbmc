import requests

def get_betweeen(original, init_str, end_str, iteration=None):
    if not iteration:
        iteration = 1
    for i in range(iteration):
        original = original[original.find(init_str)+len(init_str):]
        end = original.find(end_str)
        to_ret = original[:end]
        original = original[end:]
    return to_ret

def coger0(id):
    url = 'http://allmyvideos.net/embed-%s.html' % id
    response = requests.get(url=url)
    text = response.text
    filename = get_betweeen(text, '"file" : "', '"', iteration=2)
    return filename

def coger(session, id):
    response = session.get(url='http://allmyvideos.net/%s' % id)
    text = response.text
    """
    <Form name="F1" method="POST" action=''>
    <input type="hidden" name="op" value="download1">
    <input type="hidden" name="usr_login" value="">
    <input type="hidden" name="id" value="aqsmpv9mtfyp">
    <input type="hidden" name="fname" value="7 Vidas 13x08.avi">
    <input type="hidden" name="referer" value="">
    <input type="hidden" name="method_free" value="1">
    <input type="image"  id="submitButton" src="/images/continue-to-video.png" value="method_free" />
    <!-- <input name="confirm" type="submit" value="Continue as Free User" disabled="disabled" id="submitButton" class="confirm_button" style="width:190px;"> -->
       
    </form>
    """
    _id = get_betweeen(text, init_str='<input type="hidden" name="id" value="',
                             end_str='">')

    fname = get_betweeen(text, init_str='<input type="hidden" name="fname" value="',
                               end_str='">')

    method_free = get_betweeen(text, init_str='<input type="hidden" name="method_free" value="',
                               end_str='">')
    return  (_id, fname, method_free)
    #print response.text

def coger2(session, _id, fname, method_free):
    params = {
            'op': 'download1',
            'usr_login' : '',
            'id' : _id,
            'fname': fname,
            'referer': '',
            'method_free' : method_free,
    }
    response = session.post(url='http://allmyvideos.net/%s' % id, data=params)
    text = response.text
    print text

def get_video_by_id(id):
    return coger0(id)

def get_video_by_url(url):
    #Get the id
    id = url.split('/')[-1]
    return get_video_by_id(id)

def main():
    #print coger0('aqsmpv9mtfyp')
    pass


if __name__ == '__main__':
    main()