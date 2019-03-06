
import requests, json

url = 'https://graphql.anilist.co'


# anilist ids dont match with mal ids
def request_anilist_userlist(username):

	query = """
	query ($name: String = "%s") { # Define which variables will be used in the query (id)
	  User (name: $name) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
		id
	  }
	}
	""" % (username)

	request = requests.post(url, json={'query': query})
	# print(request)
	request = json.loads(request.content)
	query = """
	query ($userId: Int = %s) { # Define which variables will be used in the query (id)
	  MediaListCollection (userId: $userId,  type: ANIME) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
		lists {
		  name
		  isCustomList
		  isSplitCompletedList
		  status
		  entries {
			mediaId
			}
		}
	  }
	}
	""" % request['data']['User']['id']
	request = requests.post(url, json={'query': query})
	request = json.loads(request.content)
	# print(request)
	watched_anime_ids = []
	for anime_list in request['data']['MediaListCollection']['lists']:
		if anime_list['name'].lower() == 'completed':
			for entry in anime_list['entries']:

				watched_anime_ids.append(entry['mediaId'])
	
	return watched_anime_ids

# converts anilist id to mal id
def convert_anilist_to_mal(anilist_id):

	query = """
	 query ($userId: Int = %s) { # Define which variables will be used in the query (id)
      Media (id: $userId){
      idMal
    	}
  	}
	""" % (str(anilist_id))
	request = requests.post(url, json={'query': query})
	request = json.loads(request.content)

	if request.get('errors'):
		msg = request['errors']
		TF_error_handler(False, msg)

	try:
		return int(request['data']['Media']['idMal'])
	except Exception as e:
		msg = ['Error in requesting mal id from anilist.', e]
		TF_error_handler(False, msg)