import requests
from airwing_geoinfo.getgeoinfo import getGeoinfo

def generateTilelayer(service_url, workspace_name, task_id, geo_user='admin', geo_pwd='geoserver', threadCount=1, zoomStart=0, zoomStop=19):
	s = requests.Session()
	data = {
		'username': geo_user,
		'password': geo_pwd
	}
	if '/rest' in service_url:
		service_url = service_url.split('/rest')[0]
	s.post(service_url+'/j_spring_security_check', data=data, allow_redirects=False)
	latlon = getGeoinfo(service_url, workspace_name, task_id, geo_user, geo_pwd)
	payload = {
		'threadCount': threadCount,
		'type':'seed',
		'gridSetId': 'EPSG:4326',
		'format': 'image/png',
		'zoomStart': zoomStart,
		'zoomStop': zoomStop,
		'minX': latlon['left_longitude'],
		'minY': latlon['left_latitude'],
		'maxX': latlon['right_longitude'],
		'maxY': latlon['right_latitude'],
		'parameter_STYLES':'raster'
	}
	print payload
	print '*'*30
	xurl = service_url + '/gwc/rest/seed/' + workspace_name + ':' + task_id
	print xurl
	r = s.post(xurl, data=payload, allow_redirects=False)
	if r.status_code == 200:
		return 'success'
	else:
		return 'error'