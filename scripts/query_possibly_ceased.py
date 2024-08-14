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



def find_podcast_with_last_episode_harvested_before_date(my_date):
    try:
        my_time = mktime(dt.strptime(my_date, "%B %d %Y").timetuple())
        my_human_readable_date = my_date
    except ValueError:
        my_time = mktime(dt.strptime(my_date, "%d/%m/%Y").timetuple())
        my_human_readable_date = dt.strptime(my_date, "%d/%m/%Y").strftime('%B %d %Y')

    print("Selecting podcast names and mms with the last date harvested earlier than", my_human_readable_date)
    print("Machine readable time", my_time)
    print()
    
    podcasts = Podcast.select().where(Podcast.last_issue < my_time)
    dic = {}
    for pod in podcasts:
        dic[pod.last_issue] = [pod.podcast_name, pod.serial_mms, dt.fromtimestamp(pod.last_issue).strftime('%B %d %Y')]

    sorted_dic = dict(sorted(dic.items()))
    log_result = ""
    for el in sorted_dic:
        log_result += str(sorted_dic[el]) + "\n"

    return log_result




if __name__ == '__main__':
	my_date = "June 24 2024"
	my_data = "24/06/2024"
	find_podcast_with_last_episode_harvested_before_date("June 24 2024")

