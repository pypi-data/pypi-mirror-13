from . import apiUtil
from apiUtil import *

TIP_ENDPOINT = "tip"
SEPARATOR = "/"

def getResourceString(action):
	return TIP_ENDPOINT + SEPARATOR + action
	
def getTipLink(api_code):
	resource = getResourceString("tip_link")
	return call_api(resource, api_code)