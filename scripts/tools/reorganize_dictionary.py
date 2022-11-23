from podcast_dict import podcasts_dict
import podcastparser
from urllib.request import urlopen
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

"""This  script is soring pocasts dictionary by podcast name. Be carefully. Nothing should be commented in the dictionary!!!"""

#"A Neesh audience" : {'rss_filename': 'https://www.spreaker.com/show/4467635/episodes/feed', 'url': 'https://www.spreaker.com/show/a-neesh-audience', 'serial_mms': '9918987273002836', 'serial_pol': 'POL-126894', 'publish_link_ro_record': True, 'automated_flag': False, 'access_policy': '100', 'template_name': 'mis_Podcast_Neesh_audience.xml'} ,
new_dict={}
for el in podcasts_dict:
	print(el)

	new_dict[el] = dict(podcasts_dict[el])
	try:
		parsed_dict = podcastparser.parse(podcasts_dict[el]["url"], urlopen(podcasts_dict[el]["rss_filename"]))
		new_dict[el]["parsed_title"] = parsed_dict["title"]
	except:
		new_dict[el]["parsed_title"] = el
	print(new_dict[el]["parsed_title"])


temp=sorted(new_dict)
new_dict = dict([(k,new_dict[k]) for i,k in enumerate(temp)])
print(new_dict)


for el in new_dict:
 	print('"'+el+'"')
