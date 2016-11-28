import requests
import json
import Logger
logger = Logger.Logger(name='My_Logger')
def goo_shorten_url(url):
	with open('./GOOGLE_API_KEY', 'r') as f:
		google_api = f.readline().rstrip('\n')
	post_url = 'https://www.googleapis.com/urlshortener/v1/url?key={}'.format(google_api)
	payload = {'longUrl': url}
	headers = {'content-type': 'application/json'}
	r = requests.post(post_url, data=json.dumps(payload), headers=headers).json()
	if "error" in r :
		logger.addLog(r)
		return "Error"
	else : 
		return r['id']

# goo_shorten_url("https://www.google.com")