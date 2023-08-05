import requests

def getGeoinfo(service_url, user, name, data, geo_user, geo_pwd):
	s = requests.Session()
	data = {
		'username': geo_user,
		'password': geo_pwd
	}
	if '/rest' in service_url:
		service_url = service_url.split('/rest')[0]
	s.post(service_url+'/j_spring_security_check', data=data, allow_redirects=False)
	y = service_url + '/rest/workspaces/' + user + '/coveragestores/' + name + "/coverages/" + name + ".json"
	xx = s.get(y, allow_redirects=False)
	if not xx:
		return {'status': 'error'}
	else:
		geoinfo = xx.json()
		geoinfo = geoinfo['coverage']['latLonBoundingBox']
		newgeoInfo = {
			'status': 'success',
			'left_longitude': geoinfo['minx'],
			'left_latitude': geoinfo['miny'],
			'right_longitude': geoinfo['maxx'],
			'right_latitude': geoinfo['maxy']
		}
		return newgeoInfo