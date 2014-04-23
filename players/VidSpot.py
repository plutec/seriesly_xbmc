import requests

#Primera web
"""
<Form name="F1" method="POST" action=''>
<input type="hidden" name="op" value="download1">
<input type="hidden" name="usr_login" value="">
<input type="hidden" name="id" value="tvhejwllfw3s">
<input type="hidden" name="fname" value="TBBT 5x04.mp4">
<input type="hidden" name="referer" value="">
<input type="hidden" name="method_free" value="1">
<input type="image"  id="submitButton" src="/images/continue-to-video.png" value="method_free" />
<!-- <input name="confirm" type="submit" value="Continue as Free User" disabled="disabled" id="submitButton" class="confirm_button" style="width:190px;"> -->
   
</form>
"""
#En segunda
#"file" : "http://d4604.allmyvideos.net/d/zgmhrapkyq5dh6lnvpg4domlhvr2x3o7ou6jcpe3kki3uaz7olf4arwag4/video.mp4?v2",


def get_between(original, init_str, end_str, iteration=None):
    if not iteration:
        iteration = 1
    for i in range(iteration):
        original = original[original.find(init_str)+len(init_str):]
        end = original.find(end_str)
        to_ret = original[:end]
        original = original[end:]
    return to_ret

def coger(id):
	#URL CORRECTA
	# http://d4444.vidspot.net/d/ycmh2o7oyq5dh6ln5hgy3numfwgxglbf2vlyo4osyn7k42gqwhpxawaq4bvlsxq/video.mp4?v2
	session = requests.Session()

	url_original = 'http://vidspot.net/%s' % id
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
		'method_free':'1',
	}
	
	headers = {'Referer':url_original}

	response = session.post(url=url_original, headers=headers, data=data)
	text = response.text
	#print text
	to_ret = get_between(original=text,
						 init_str='"file" : "',
						 end_str='",',
						 iteration=2)
	#print '*'*80
	return to_ret


def get_video_by_id(id):
    return coger(id)

def get_video_by_url(url):
    #Get the id
    id = url.split('/')[-1]
    return get_video_by_id(id)

def main():
	print get_video_by_url('http://www.vidspot.net/tvhejwllfw3s')

if __name__ == '__main__':
	main()