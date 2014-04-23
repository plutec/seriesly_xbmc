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

def coger(id):
	#Correcta
	#http://e2.magnovideo.com:8080/storage/files/0/9/63/156/ -> Server pero sin part1
	#1.mp4 -> file
	#?burst=6519k&u=600k&md=mq7ThMPUedF3ie8BMWuZtg&e=1390026537 -> Todo lo demas ok


	#http://o1.magnovideo.com:8080/storage/files/part1/0/9/63/156/1.mp4?burst=6519k&u=600k&md=SzYHzCjjGOSBeUE8D-4RUw&e=1390026188
	#http://e2.magnovideo.com:8080/storage/files/0/9/63/156/1.mp4?burst=6519k&u=600k&md=I7RPNk9AA3cBPPVWL_ffuQ&e=1390027084
	#$f = file_get_contents('http://www.magnovideo.com/player_config.php?mdid='.$_GET['mv']);
	session = requests.Session()
	session.get(url='http://www.magnovideo.com/?v=%s' % id)
	response = session.get(url='http://www.magnovideo.com/player_config.php?mdid=%s' % id)
	text = response.text

	#$data = array();
	data = dict()


	#preg_match('#\<original_storage_path\>(.+)\</original_storage_path\>#i', $f, $temp);
	#$data['server'] = $temp[1];
	data['server'] = get_betweeen(original=text, init_str='<storage_path>',
										end_str='</storage_path>') #OK


	#preg_match('#\<tile_thumbs\>'.preg_quote($data['server']).'/(.+)/tmpsmall/#i', $f, $temp);
	#$data['folder'] = $temp[1].'/';
	#data['folder'] = 'http://o1.magnovideo.com:8080//storage/files/part1/0/9/63/156/'
	data['folder'] = get_betweeen(original=text, init_str='<tile_thumbs>',
										end_str='</tile_thumbs>')

	tmp = data['folder'].split('/')
	tmp = tmp[:-2]
	tmp2 = list()
	for i in range(len(tmp)):
		path = tmp[i]
		if path.find('part') == -1:
			tmp2.append(path)
	tmp2.append('')
	tmp = tmp2
	tmp = tmp[3:]
	#print tmp
	data['folder'] = '/'.join(tmp)
	#print data['folder']


	#preg_match('#\<video_name\>(.+)\</video_name\>#i', $f, $temp);
	#$data['file'] = $temp[1];
	data['file'] = get_betweeen(original=text, init_str='<video_name>',
										end_str='</video_name>')


	#preg_match('#\<movie_burst\>([0-9]+)\</movie_burst\>#i', $f, $temp);
	#$data['burst'] = $temp[1];
	data['burst'] = get_betweeen(original=text, init_str='<movie_burst>',
										end_str='</movie_burst>')


	#preg_match('#\<burst_speed\>([0-9]+)\</burst_speed\>#i', $f, $temp);
	#$data['burst_speed'] = $temp[1];
	data['burst_speed'] = get_betweeen(original=text, init_str='<burst_speed>',
										end_str='</burst_speed>')


	#preg_match('#\<ste\>(.+)\</ste\>#i', $f, $temp);
	#$data['ste'] = $temp[1];
	data['ste'] = get_betweeen(original=text, init_str='<ste>',
										end_str='</ste>')


	#unset($temp, $f);


	#echo '<pre>', print_r($data), '</pre>', $data['server'], $data['folder'], $data['file'], '?burst=', $data['burst'], 'k&u=', $data['burst_speed'], 'k&', $data['ste'];
	#echo '<pre>', print_r($data), '</pre>', 
	return data['server'] + data['folder'] + data['file'] + '?burst=' + data['burst'] + 'k&u=' + data['burst_speed'] + 'k&' + data['ste']

def get_video_by_id(id):
    return coger(id)

def get_video_by_url(url):
    #Get the id
    id = url.split('=')[-1]
    return get_video_by_id(id)

def main():
	#print coger('FGPEU72')
	print get_video_by_url('http://www.magnovideo.com/?v=RALOMJFR')
if __name__ == '__main__':
	main()