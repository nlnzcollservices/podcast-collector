import requests
from podcast_dict import podcasts_dict
count = 0

for el in podcasts_dict:
	# print(el)
	try:
		r = requests.get(podcasts_dict[el]["rss_filename"],allow_redirects = True)

	except Exception as e:
		print(el)
		print(str(e))
		print (podcasts_dict[el]["rss_filename"])
	if r.status_code!=200:
		count+=1
		print(count)
		print(el)
		print(r.status_code)
		print(podcasts_dict[el]["rss_filename"])
