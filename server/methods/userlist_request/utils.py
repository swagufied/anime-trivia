import requests
import random
import time
import json
import sys
from bs4 import BeautifulSoup


api_url_base = "https://api.jikan.me/"

MAX_TRIES = 3
MIN_SLEEP = 1


#input username of user list you want to get
#returns beautiful soup of the user's anime list.
def request_userlist(username, api_url):

	# api_url = "http://myanimelist.net/malappinfo.php?u={}&status=all&type=anime".format(username)
	
	response = make_request(api_url)

	if response.status_code == 200:
		return BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
	else:
		return None

# makes request to jikan api. input id and type of info you're looking for
def request_api(api_url):

	response = make_request(api_url)

	if response.status_code == 200:
		# if 'error' in response:
		# 	raise Exception("error in call to '{}': {}".format(api_url, response))

		return json.loads(response.text)

	elif response.status_code == 429:
		print('too many requests')

		return None
		

	else:
		return None

def request_page(url):
	response = make_request(url)
	if response.status_code == 200:
		return response.content.decode('utf-8')

	elif response.status_code == 429:
		print('too many requests')
		return None
		

	else:
		return None

def request_xml_api(url):
	response = make_request(url)
	if response.status_code == 200:
		return response.content

	elif response.status_code == 429:
		print('too many requests')
		return None
		
	else:
		return None
	

# makes the api request MAX_TRIES times with at least MIN_SLEEP time between each request
def make_request(api_url):
	
	#make initial request
	sleep_time = MIN_SLEEP
	print('requesting: {}'.format(api_url))
	time.sleep(sleep_time)
	response = requests.get(api_url)

	tries = 0

	while(response.status_code != 200 and tries < MAX_TRIES):

		sleep_time = MIN_SLEEP
		time.sleep(sleep_time)
		print('requesting: {}'.format(api_url))
		response = requests.get(api_url)

		tries += 1

	return response