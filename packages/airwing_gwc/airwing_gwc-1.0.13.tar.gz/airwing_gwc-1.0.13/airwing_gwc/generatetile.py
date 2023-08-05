import requests
from airwing_geoinfo.getgeoinfo import getGeoinfo

def generateTilelayer(service_url, workspace_name, task_id, geo_user='admin', geo_pwd='geoserver', threadCount=1, zoomStart=0, zoomStop=19):
    s = requests.Session()
    data = {
        'username': geo_user,
        'password': geo_pwd
    }
    s.post(service_url+'/j_spring_security_check', data=data, allow_redirects=False)
    latlon = getGeoinfo(service_url, workspace_name, task_id, geo_user, geo_pwd)
    payload = {
        'threadCount': threadCount,
        'type': 'seed',
        'gridSetId': 'EPSG:900913',
        'format': 'image/png',
        'zoomStart': zoomStart,
        'zoomStop': zoomStop,
        'minX': latlon['left_longitude'],
        'minY': latlon['left_latitude'],
        'maxX': latlon['right_longitude'],
        'maxY': latlon['right_latitude'],
        'parameter_STYLES': 'raster'
    }
    xurl = service_url + '/gwc/rest/seed/' + workspace_name + ':' + task_id
    res = s.post(xurl, data=payload, allow_redirects=False)
    print '--------------- Response from generating tile layers API ---------------'
    print res.text
    print '--------------- End of response ---------------'
    if res.status_code == 200:
        return {
            'status': 'success'
        }
    else:
        return {
            'status': 'error',
            'reason': '%d error' % res.status_code
        }

def queryStatus(service_url, workspace_name, task_id, geo_user='admin', geo_pwd='geoserver'):
    s = requests.Session()
    data = {
        'username': geo_user,
        'password': geo_pwd
    }
    s.post(service_url+'/j_spring_security_check', data=data, allow_redirects=False)
    xurl = service_url + '/gwc/rest/seed/' + workspace_name + ':' + task_id + '.json'
    r = s.get(xurl).json()
    if r['long-array-array'] != []:
        if r['long-array-array'][0][4] == -1:
            r['long-array-array'][0][4] = 'ABORTED'
        elif r['long-array-array'][0][4] == 0:
            r['long-array-array'][0][4] = 'PENDING'
        elif r['long-array-array'][0][4] == 1:
            r['long-array-array'][0][4] = 'RUNNING'
        elif r['long-array-array'][0][4] == 2:
            r['long-array-array'][0][4] = 'DONE'

        return {
            'tiles processed': r['long-array-array'][0][0],
            'total of tiles to process': r['long-array-array'][0][1],
            'expected remaining time in seconds': r['long-array-array'][0][2],
            'Task ID': r['long-array-array'][0][3],
            'Task status': r['long-array-array'][0][4]
        }
    else:
        return {
            'Task status':'NULL'
        }