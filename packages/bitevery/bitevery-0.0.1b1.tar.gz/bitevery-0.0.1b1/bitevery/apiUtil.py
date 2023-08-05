import sys

BASE_URL = "http://www.bitevery.com/api"
SEPARATOR = "/"

py_version = sys.version_info[0]
if py_version >= 3:
    # Python 3.0 and later
    from urllib.request import urlopen
    from urllib.error import HTTPError
else:
    # Python 2.x
    from urllib2 import urlopen
    from urllib2 import HTTPError

def call_api(resource, api_code, data = None):
	request = BASE_URL + SEPARATOR + resource + SEPARATOR + str(api_code)
	try:
		return urlopen(request).read()
	except HTTPError as e:
		return "HTTP error: " + e.read() + ", error code:" + e.code
		
	
	