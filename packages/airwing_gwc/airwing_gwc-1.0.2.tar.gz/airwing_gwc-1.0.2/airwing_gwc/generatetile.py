import requests

def generateTilelayer(service_url, geo_user, geo_pwd, workspace_name, task_id, threadCount=1, zoomStart=0, zoomStop=19):
	s = requests.Session()
	data = {
		'username': geo_user,
		'password': geo_pwd
	}
	s.post(service_url+'/j_spring_security_check', data=data, allow_redirects=False)
	surl = service_url + '/gwc/rest/layers/' + workspace_name + ':' + task_id + '.json'
	print surl
	t = s.get(surl, allow_redirects=False)
	x = t.json()
	coords = x['GeoServerLayer']['gridSubsets'][1]['extent']['coords']
	payload = {
		'threadCount': threadCount,
		'type':'seed',
		'gridSetId': 'EPSG:4326',
		'format': 'image/png',
		'zoomStart': zoomStart,
		'zoomStop': zoomStop,
		'minX': coords[0],
		'minY': coords[1],
		'maxX': coords[2],
		'maxY': coords[3],
		'parameter_STYLES':'raster'
	}
	xurl = service_url + '/gwc/rest/seed/' + workspace_name + ':' + task_id
	r = s.post(xurl, data=payload, allow_redirects=False)
	if r.status_code == 200:
		return 'success'
	else:
		return 'error'