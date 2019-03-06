from .utils import request_api

base_url = "https://api.jikan.moe/v3"

def request_mal_userlist(username):

	anime_list = request_api(base_url + '/user/{}/animelist/completed'.format(username))
	# print(anime_list)
	if 'error' in anime_list:
		# print(anime_list)
		return anime_list

	anime_ids = []
	for anime in anime_list['anime']:
		if anime['type'].lower() in ['tv', 'movie']:
			anime_ids.append(anime['mal_id'])

	return anime_ids