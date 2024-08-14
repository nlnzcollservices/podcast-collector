import peewee
import requests
import re
import sys
from podcast_models import Podcast, Episode, File
from datetime import datetime as dt
from time import mktime
import datetime as DT
from datetime import time
from bs4 import BeautifulSoup as bs
from podcast_dict import podcasts_dict
from alma_tools import AlmaTools
import os
sys.path.insert(0, r'H:\GIT\file-downloader')
from downloader_light_modified import DownloadResource as Downloader

my_files = []
my_api = AlmaTools("prod")
my_time  = mktime(dt.strptime('September 01 2021', "%B %d %Y").timetuple())
print(my_time)


my_dict={}
big_dict={}
count = 0
#podcasts = Podcast.select()#.where(Podcast.podcast_name == "Access Granted NZ")

my_list = []
podcasts = Podcast.select()#.where(Podcast.last_issue < 1685534400.0)



def split_rss_title(podcast_name, episode_title, epis_numb, epis_seas):
	bib_title = None
	bib_numbering = None

	if podcast_name in ["CIRCUIT cast"]:
	    if ":" in episode_title:
	        bib_title = ":".join(episode_title.split(":")[1:]).lstrip(" ")
	        bib_numbering = episode_title.split(":")[0]
	    elif "-" in episode_title:
	        bib_title = "-".join(episode_title.split("-")[1:]).lstrip(" ").rstrip(" ")
	        bib_numbering = episode_title.split("-")[0].lstrip(" ")

	if podcast_name in ["Dirt Church Radio"]:
	    if "-" in episode_title:
	        bib_title = episode_title.lstrip("DCR").lstrip(" ").split("-")[-1].lstrip(" ")
	        bib_numbering = episode_title.split("-")[0].rstrip(" ")

	if podcast_name in ["Advanced analytics"]:
	    if ":" in episode_title:
	        bib_title = episode_title.split(":")[-1].lstrip(" ")
	        bib_numbering = episode_title.split(":")[0].rstrip(" ")

	if podcast_name in ["Kiwi birth tales"]:
	    if ":" in episode_title:
	        bib_title = ":".join(episode_title.split(":")[1:]).lstrip(" ")
	        bib_numbering = episode_title.split(":")[0].rstrip(" ")
	    elif "-" in episode_title:
	        bib_title = "-".join(episode_title.split("-")[1:]).lstrip(" ")
	        bib_numbering = episode_title.split("-")[0].rstrip(" ")

	if podcast_name in ["Taringa", "Dancing in your head"]:
		if "- Ep" in episode_title:
		    bib_title = " - ".join(episode_title.split(" - ")[2:]).rstrip(" ").lstrip(" ")
		    bib_numbering = episode_title.split(" - ")[1].lstrip(' ').rstrip(" ").replace(" |", ",")


	if podcast_name in ["All Blacks"]:
		if episode_title.startswith("Episode") and episode_title.split(" ")[2].startswith("S"):
			bib_title = " ".join(episode_title.split(" ")[3:])
			bib_numbering = " ".join(episode_title.split(" ")[:3])

	if podcast_name in ["DOC sounds of science podcast"]:
	    if ":" in episode_title:
	        bib_title = ":".join(episode_title.split(":")[1:]).lstrip(" ")
	        bib_numbering = episode_title.split(":")[0].rstrip(" ")
	    if bib_numbering:
	        try:
	            if not "episode" in bib_numbering.lower() and not "ep" in bib_numbering.lower() and not bib_numbering.lower().startswith("e") and not "podcast" in bib_numbering.lower():
	                bib_numbering = "Episode " + bib_numbering
	        except:
	            bib_numbering = None

	if podcast_name in ["76 small rooms", "History of Aotearoa New Zealand podcast", "Dirt Church Radio"]:
		if "-" in episode_title:
			bib_title = "-".join(episode_title.split("-")[1:]).lstrip(" ")
			bib_numbering = episode_title.split("-")[0].rstrip(" ")
			if not bib_numbering and epis_numb:
				bib_numbering = "Episode " + epis_numb

	if podcast_name in ["The real pod", "Taxpayer talk", "The fold"]:
	    if ":" in episode_title:
	        bib_title = ":".join(episode_title.split(":")[1:]).lstrip(" ")

	if podcast_name in ["Better off read"]:
	    if "Ep " in episode_title or "Episode" in episode_title:
	        bib_title = " ".join(episode_title.split(" ")[2:])
	        bib_numbering = " ".join(episode_title.split(" ")[:2]).rstrip(":")

	if podcast_name in ["The Angus Dunn"]:
	    if "The Angus Dunn Podcast " in my_alma.xml_response_data:
	        bib_title = my_rec["245"]["a"].lstrip("The Angus Dunn Podcast ")
	        if "-" in bib_title:
	            divider = "-"
	        if ":" in bib_title:
	            divider = ":"
	        bib_numbering = bib_title.split(divider)[0]

	if podcast_name in ["Business is boring"]:
	    if "Business is boring" in episode_title:
	        bib_title = episode_title.lstrip("Business is boring").lstrip(" ").lstrip(":").lstrip(" ")
	    if "Business is Boring" in episode_title:
	        bib_title = episode_title.lstrip("Business is Boring").lstrip(" ").lstrip(":").lstrip(" ")

	if podcast_name in ["TOA Tabletop"]:
	    if ":" in episode_title:
	        if episode_title.split(":")[0].isdigit():
	            bib_title = ":".join(episode_title.split(":")[1:]).lstrip(" ")
	            bib_numbering = episode_title.split(":")[0].rstrip(' ')

	if podcast_name in ["Stag roar"]:
	    if ":" in episode_title:
	        bib_title = ":".join(episode_title.split(":")[1:]).lstrip(" ")
	        bib_numbering = episode_title.split(":")[0].rstrip(' ')
	    elif '-' in episode_title:
	        bib_title = "-".join(episode_title.split("-")[1:]).lstrip(" ")
	        bib_numbering = episode_title.split("-")[0].rstrip(' ')

	if podcast_name in ["Dr. Tennant's verbal highs"]:
	    if ":" in episode_title:
	        bib_title = ":".join(episode_title.split(":")[1:]).lstrip(" ")
	        bib_numbering = episode_title.split(":")[0].rstrip(' ')

	if podcast_name in ["Girls on top"]:
	    if "-" in episode_title and episode_title.startswith("Episode"):
	        bib_title = "-".join(episode_title.split("-")[1:]).lstrip(" ")
	        bib_numbering = episode_title.split("-")[0].rstrip(' ')

	if podcast_name in ["Untamed Aotearoa"]:
	    if "#" in episode_title:
	        bib_title = "#".join(episode_title.split("#")[1:]).lstrip(" ")
	        bib_numbering = "# " + episode_title.split("#")[0].rstrip(' ')

	if podcast_name in ["NZ tech podcast with Paul Spain"]:
	    if ":" in episode_title and ("NZ Tech Podcast" in episode_title or "Episode" in episode_title) and not "Running time" in episode_title:
	        ep_number = None
	        if ": NZ Tech Podcast" in episode_title:
	            bib_title = ":".join(episode_title.split(":")[:-1])
	            ep_number = re.findall(r'[0-9]+', episode_title.split(":")[-1])[0]
	        elif "NZ Tech Podcast" in episode_title:
	            bib_title = ":".join(episode_title.split(":")[1:])
	            try:
	                ep_number = re.findall(r'[0-9]+', episode_title.split(":")[0])[0]
	            except:
	                logger.info("no episode number")
	        elif ": Episode" in episode_title:
	            ep_number = re.findall(r'[0-9]+', episode_title.split(":")[1])[0]
	        elif episode_title.startswith("Episode"):
	            ep_number = re.findall(r'[0-9]+', episode_title.split(":")[0])[0]

	    elif "- NZ Tech Podcast" in episode_title:
	        bib_title = "-".join(episode_title.split(":")[:-1])

	if podcast_name in ["Stirring the pot", "UC science radio"]:
		bib_title = str(episode_title)
		if epis_numb:
			bib_title = episode_title.strip(epis_numb).rstrip(" ").lstrip(" ")
			if epis_seas:
				bib_numbering = "S{}:E{}".format(epis_seas, epis_numb)
			else:
				bib_numbering ="Episode " +  epis_numb

	if podcast_name in ["Queenstown life", "Windows on dementia"]:
	    bib_numbering = "Episode " + epis_numb

	if podcast_name in ["Property Academy"]:
	    if "⎮" in episode_title:
	        divider = "⎮"
	    else:
	        divider = "|"
	    bib_title = "|".join(episode_title.split(divider)[:-1])
	    bib_numbering = episode_title.split(divider)[-1]

	if podcast_name == "Chris and Sam podcast":
	    bib_title = episode_title.split(" | ")[0]
	    if " | EP" in episode_title:
	        bib_numbering = "EP" + episode_title.split("EP")[1].split(" ")[0]
	    elif "EP" in episode_title:
	        bib_title = episode_title.split("EP")[0]
	        if " - " in episode_title:
	            bib_numbering = "EP" + episode_title.split("EP")[1].split(" - ")[0]

	if podcast_name in  ["Dont give up your day job"]:
			bib_title  = " ".join(episode_title.split(" ")[1:])
			bib_numbering = "Episode " + episode_title.split(" ")[0].rstrip(".")

	if podcast_name in ["thehappy$aver.com."]:
	    if "." and episode_title and episode_title.split(".")[0].isdigit():
	        bib_title = ".".join(episode_title.split(".")[1:]).lstrip(" ")
	        bib_numbering = "Episode " + episode_title.split('.')[0]

	if podcast_name in ["B better podcast"]:
			if episode_title.startswith("#"):
				bib_title = " ".join(episode_title.split(" ")[1:]).lstrip(" ")
				bib_numbering = episode_title.split(" ")[0]


	if podcast_name in ["NUKU 100"]:
			if episode_title.startswith("//"):
				bib_title = " ".join(episode_title.split(" ")[1:]).lstrip(" ")
				bib_numbering = "Episode "+episode_title.split(" ")[0].lstrip("//")

	if not bib_title:

	    bib_title = str(episode_title)

	dot_or_something = "."
	if bib_title.startswith(dot_or_something):
	    bib_title = bib_title.lstrip(dot_or_something).lstrip(" ")
	if bib_title.rstrip(" ").endswith("?") or bib_title.rstrip(" ").endswith("!") or bib_title.rstrip(" ").endswith("."):
		dot_or_something = ""
	bib_title = bib_title + dot_or_something


	return (bib_title, bib_numbering)



for pod in podcasts:


		if "Dancing in your head" in pod.podcast_name:
			print(pod.podcast_name)

		# 	# print("#"*50)
			print(pod.serial_mms)
			print(pod.serial_pol)
			print(pod.serial_holding)
			print(pod.location)
			print(pod.rss_link)
			print(pod.serial_mms)
			print(pod.automated_flag)
			print (pod.serial_pol)
			print(pod.last_issue)
			# q = Podcast.update(last_issue = 1630411200.0).where(Podcast.id == pod.id)
			# q.execute()
			try:
				print(dt.fromtimestamp(pod.last_issue).strftime('%B %d %Y'))
			except Exception as e:
				print(str(e))
			episodes = Episode.select().where(Episode.podcast==pod.id)

			# # q = Podcast.update(last_issue = 1620129600.0).where(Podcast.id == pod.id)
			# # q.execute()
			for ep in episodes:	

						bib_title, bib_numbering = split_rss_title(pod.podcast_name, ep.episode_title, ep.epis_numb, ep. epis_seas)
					#if bib_numbering:
						print(ep.id)
						print(ep.episode_title)

						q = Episode.update(bib_title = bib_title, bib_numbering= bib_numbering).where(Episode.id == ep.id)
						q.execute()

						print(ep.bib_title)
						print(bib_title)
						print(ep.bib_numbering)
						print(bib_numbering)
						print(ep.ie_num)
						print(ep.item)
						print(ep.tick)
						print(ep.mis_mms)
						print(ep.harvest_link)
						print(ep.updated)
						print(ep.sip)
						print(ep.description)
						print(ep.tags)
						print(ep.episode_link)

