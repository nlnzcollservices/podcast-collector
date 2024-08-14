import peewee
import requests
import re
import sys
from io import StringIO
from settings_prod import logging, template_folder,start_xml, end_xml, report_folder
from fuzzywuzzy import fuzz




from podcast_models import Podcast, Episode, File

from datetime import datetime as dt
from time import mktime
import datetime as DT
from datetime import time
from bs4 import BeautifulSoup as bs
from podcast_dict import podcasts_dict
import feedparser
import podcastparser
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

# my_api.get_set_members("13958631030002836",{"limit":"100","offset":"100"})
# mms_ids = re.findall(r"id>(.*?)</id",my_api.xml_response_data)


with open("update_log1.txt","r") as f:
	data=f.read()
my_dict = {}
for el in data.split("\n")[:-1]:
	mms = el.split("||")[0]
	link = el.split("||")[1]
	if link in my_dict.keys():
		my_dict[link]+=[mms]
	else:
		my_dict[link]= [mms]
mms_ids = []
for el in my_dict.keys():
	if len(my_dict[el] )>1:
		print(el)
		print(my_dict[el])
		mms_ids+=my_dict[el]
print(mms_ids)
quit()
my_alma = AlmaTools("prod")
message = ""
for mms in mms_ids:
	print("#"*50)
	print("#"*50)
	my_alma.get_bib(mms)
	my_xml=my_alma.xml_response_data
	xml_object = StringIO(my_xml)
	my_record = parse_xml_to_array(xml_object)[0]
	#print(my_record)
	f856s=my_record.get_fields("856")
	harvest_link = ""
	episode_link = ""
	if len(f856s)==3:
		for idx in range(len(f856s)):
			subfields = f856s[idx].subfields
			indicators = f856s[idx].indicators
			#For updates to exlude automated field
			for sld in subfields:
				if sld.code == "z":
					field3 = f856s[idx]
		f490 = my_record.get_fields("490")[0].subfields[0].value.rstrip(",.;")
		f245 = my_record.get_fields("245")[0].subfields[0].value.rstrip(",.;")
		print(f490)
		for el in podcasts_dict.keys():
			print(el)

			levenshtein_distance = fuzz.ratio(el, f490)
			if levenshtein_distance >60:
				print("HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1")

				rss_link = podcasts_dict[el]["rss_filename"]
				url = podcasts_dict[el]["url"]
				harvest_link = str(rss_link)
				episode_link = str(url)
		d = feedparser.parse(rss_link)
		for ind in range(len(d["entries"])):
			title = d["entries"][ind]["title"]
			print(d["entries"][ind]["links"])

		
			# print(f245)
			# print(title)
			levenshtein_distance = fuzz.ratio(f245, title)
			# print(levenshtein_distance)

			if levenshtein_distance >80:
				title = str(245)
				harvest_link = d["entries"][ind]["links"][0]["href"]
				try:
					episode_link = d["entries"][ind]["links"][1]["href"]
				except:
					print("NO episode_link")
		indicators1 = ['4', '0']
		indicators2 = ['4', '2']
		subfields1 = [Subfield(code='u', value=harvest_link)]
		subfields2 = [Subfield(code='3', value='File host'), Subfield(code='u', value=episode_link)]
		field1 = Field(tag = "856", indicators = indicators1, subfields = subfields1)	
		field2 = Field(tag = "856", indicators = indicators2, subfields = subfields2)
		field3 = my_record.get_fields("856")[-1]
		my_record.remove_fields("856")
		my_record.add_ordered_field(field1)
		if episode_link != "":
			my_record.add_ordered_field(field2)
		my_record.add_ordered_field(field3)
		message  = harvest_link +"||"+episode_link
		print(my_record)
		bib_data = record_to_xml(my_record)
		bib_data = str(bib_data).replace("\\n", "\n").replace("\\", "")
		bib_data = start_xml + bib_data +end_xml
		my_alma.update_bib(mms, bib_data)
		print(my_alma.xml_response_data)
	with open("update_log1.txt","a") as f:
		f.write(mms+"||"+message+"\n")