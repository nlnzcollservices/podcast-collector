import peewee
import requests
import re
import sys
sys.path.insert(0, r"Y:\ndha\pre-deposit_prod\LD_working\podcasts\scripts")
sys.path.insert(0, "Y:\ndha\pre-deposit_prod\LD_working\podcasts\database")

from podcast_models import Podcast, Episode, File

from datetime import datetime as dt
from time import mktime
import datetime as DT
from datetime import time
from bs4 import BeautifulSoup as bs
from podcast_dict import podcasts_dict
sys.path.insert(0, r"Y:\ndha\pre-deposit_prod\LD_working\alma_tools")
from alma_tools import AlmaTools
import os
sys.path.insert(0, r'H:\GIT\file-downloader')
from downloader_light_modified import DownloadResource as Downloader
from pymarc import parse_xml_to_array,record_to_xml, Field, Subfield

my_files = []
my_api = AlmaTools("prod")
my_time  = mktime(dt.strptime('June 01 2023', "%B %d %Y").timetuple())
print(my_time)
#quit()

my_alma = AlmaTools("prod")
podcasts = Podcast.select()#.where(Podcast.podcast_name == "Access Granted NZ")
for pod in podcasts:
			episodes = Episode.select().where(Episode.podcast==pod.id)
			
			for ep in episodes:
				
				if ep.date > 1685534400.0 and ep.mis_mms:#ep.ie_num:
				#if ep.id in [15992]:
						print("-"*50)
						print(pod.podcast_name)
						# print(pod.serial_mms)
						print(ep.id)
						print(ep.episode_title)
						print(ep.harvest_link)
						print(ep.episode_link)
						print(ep.date_harvested)
						print(ep.mis_mms)
						my_alma.get_bib(ep.mis_mms)
						print(my_alma.xml_response_data)
						# print(ep.episode_title)
						