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
import os

#change the date here 

my_numan_readable_date = 'January 01 2023'
my_time  = mktime(dt.strptime(my_numan_readable_date, "%B %d %Y").timetuple())

print("Selecting podcast names and mms with the last date harvested earlier than",my_numan_readable_date)
print("Machine readable time", my_time)
print()
podcasts = Podcast.select().where(Podcast.last_issue < my_time)
dic ={}
for pod in podcasts:
	
	dic[pod.last_issue] = [pod.podcast_name,pod.serial_mms,dt.fromtimestamp(pod.last_issue).strftime('%B %d %Y')]

sorted_dic =  dict(sorted(dic.items()))			
for el in sorted_dic:
	print(sorted_dic[el])
