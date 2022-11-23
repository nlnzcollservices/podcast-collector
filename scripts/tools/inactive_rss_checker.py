import requests
from inactive_podcast_dict import inactive_podcast_dict
import feedparser
# import urllib3

#This command disables Insercure Request warnings
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

count = 0

for el in inactive_podcast_dict:
	# print("-"*50)
	# print(inactive_podcast_dict[el]["rss_filename"])
	try:
		r = requests.get(inactive_podcast_dict[el]["rss_filename"],allow_redirects = True,verify=False)

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
		print(inactive_podcast_dict[el]["url"])
		print(inactive_podcast_dict[el]["rss_filename"])

		# with open("status_codes.txt", 'a', encoding="utf-8") as f:
		# 	f.write('%s|%s|%s|%s\n' % (el,r.status_code,inactive_podcast_dict[el]["url"],inactive_podcast_dict[el]["rss_filename"]))
		
	else:
		if inactive_podcast_dict[el]["rss_filename"] != "":

			d = feedparser.parse(inactive_podcast_dict[el]["rss_filename"])
			if len(d["entries"]) <10000 and len(d["entries"])>0:
				print("-"*50)
				print("Lenght of rss", len(d["entries"]))
				print(inactive_podcast_dict[el]["url"])

				print("Latest date")
				episode_date = d["entries"][0]["published"]
				print(episode_date)
				print("Earliest date")
				episode_date = d["entries"][-1]["published"]
				print(episode_date)

			elif len(d["entries"])==0:
				print("#"*50)
				print("Lenght of rss", len(d["entries"]))
		pass
