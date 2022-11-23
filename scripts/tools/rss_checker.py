import requests
from podcast_dict import podcasts_dict
import feedparser
count = 0

for el in podcasts_dict:
	# print("-"*50)
	# print(podcasts_dict[el]["rss_filename"])
	try:
		r = requests.get(podcasts_dict[el]["rss_filename"],allow_redirects = True)

	except Exception as e:
		pass
		# print(el)
		# print(str(e))
	if r.status_code!=200:
		count+=1
		print("-"*50)
		# print(count)
		print(el)
		print(r.status_code)
		print(podcasts_dict[el]["url"])
		print(podcasts_dict[el]["rss_filename"])
		
	else:
		# if podcasts_dict[el]["rss_filename"] != "":

		# 	d = feedparser.parse(podcasts_dict[el]["rss_filename"])
		# 	if len(d["entries"]) <10000 and len(d["entries"])>0:
		# 		print("-"*50)
		# 		print("Lenght of rss", len(d["entries"]))
		# 		print(podcasts_dict[el]["url"])

		# 		print("Latest date")
		# 		episode_date = d["entries"][0]["published"]
		# 		print(episode_date)
		# 		print("Earliest date")
		# 		episode_date = d["entries"][-1]["published"]
		# 		print(episode_date)

		# 	elif len(d["entries"])==0:
		# 		print("#"*50)
		# 		print("Lenght of rss", len(d["entries"]))
		pass
