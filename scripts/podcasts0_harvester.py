import os
import sys
import re
import feedparser
import podcastparser
import subprocess
import gspread

sys.path.insert(0, r"Y:\ndha\pre-deposit_prod\LD_working\alma_tools")
from alma_tools import AlmaTools
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from time import time, sleep, mktime
from datetime import datetime as dt
from podcast_dict import podcasts_dict, serials
from podcasts_database_handler import DbHandler
from nltk.corpus import words
import nltk
from datetime import datetime
import dateparser

nltk.download('words')
##################################SSL  problem########################################
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context
ssl._create_default_https_context = ssl._create_unverified_context
##############################################################################
from settings import  file_folder, report_folder, podcast_sprsh, logging,creds, downloader_folder
sys.path.insert(0, downloader_folder)
from downloader_light_modified import DownloadResource as Downloader
logger = logging.getLogger(__name__)

#######################################Creating google spreadsheet object#################################################


c = gspread.authorize(creds)
gs = c.open_by_key(podcast_sprsh)
#change if the name or id of the worksheet is different
ws = gs.get_worksheet(0)



	
class Harvester():

	"""
		This class manages harvesting podcast episodes via rss feed.

		Attributes
		----------

	    podcast_name(str) - name of podcast from podcasts_dict. Should be the same as in serial_record
	    podcast_data(dict) - dictionary which contains information about particular podcast
	    podcast_id(int) - id of podcast in db
	    podcast_url(str) - link to podcast web page


	 	Methods
		-------
		__init__(self, podcast_id, podcast_name, podcast_data, last_issue)
		reload_spreadsheet(self, function, parameters)
		episode_sprsh_check(self)
		jhove_check(self, filepath)
		find_description_with_podcastparser(self)
		find_download_link_with_podcastparser(self)
		parsing_with_feedparser(self)
		check_for_meaning(self, my_filename)
	"""

	def __init__(self, podcast_id, podcast_name, podcast_data, last_issue, podcast_url, serial_mms):
		

		self.podcast_id = podcast_id
		self.podcast_name = podcast_name
		self.serial_mms = serial_mms
		self.podcast_data = podcast_data
		self.last_issue = last_issue
		self.podcast_url = podcast_url
		self.download_flag = False
		self.flag_for_podc_table = True
		self.episode_title = None
		self.bib_title = None
		self.bib_numbering = None
		self.rss_filename = None
		self.description = None
		self.description2 = None
		self.epis_numb = None
		self.description = None
		self.description2 = None
		self.epis_seas = None
		self.tags = None
		self.time_flag= False
		self.tags_list = ""	
		self.link_dict = {}	
		self.episode_download_link = None
		self.episode_link = None
		self.f_path = None
		self.file_dictionary = None
		self.flag_for_epis_table = False
		self.flag_for_file = False
		self.spreadsheet_message = ""
		self.rss_filename = None

	def reload_spreadsheet(self):

		c = gspread.authorize(creds)
		gs = c.open_by_key(podcast_sprsh)
		ws = gs.get_worksheet(0)
		rng = "D2:D{}".format(ws.row_count)	
		cell_range = ws.range(rng)
		return cell_range
	

	def extract_episode_info(self, text, pattern):
	    match = pattern.search(text)
	    if match:
	        ep_info = match.group(1)
	        # Extract the rest of the string excluding the episode information
	        remaining_text = pattern.sub('', text).strip()
	        return remaining_text, ep_info
	    return text, None


	def split_rss_title(self):
		self.bib_title = None
		self.bib_numbering = None

		if self.podcast_name in ["CIRCUIT cast"]:
			if ":" in self.episode_title:
				self.bib_title = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
				self.bib_numbering = self.episode_title.split(":")[0]
			elif "-" in self.episode_title:
				self.bib_title= "-".join(self.episode_title.split("-")[1:]).lstrip(" ").rstrip(" ")
				self.bib_numbering = self.episode_title.split("-")[0].lstrip(" ")

		if self.podcast_name in ["Advanced analytics"]:
			if ":" in self.episode_title:
				self.bib_title = self.episode_title.split(":")[-1].lstrip(" ")
				self.bib_numbering = self.episode_title.split(":")[0].rstrip(" ")
		

		if self.podcast_name in ["Taringa", "Dancing in your head"]:
			if "- Ep" in self.episode_title:
				if not self.episode_title.split(" ")[-1].startswith("Ep"):
					self.bib_title = " - ".join(self.episode_title.split(" - ")[2:]).rstrip(" ").lstrip(" ")
					self.bib_numbering = self.episode_title.split(" - ")[1].lstrip(' ').rstrip(" ").replace(" |",",")
				

		if self.podcast_name in ["All Blacks"]:
			if self.episode_title.startswith("Episode") and self.episode_title.split(" ")[2].startswith("S"):
				self.bib_title = " ".join(self.episode_title.split(" ")[3:])
				self.bib_numbering = " ".join(self.episode_title.split(" ")[:3])

		if self.podcast_name in ["DOC sounds of science podcast"]:
			if ":" in self.episode_title: 
				self.bib_title = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
				self.bib_numbering = self.episode_title.split(":")[0].rstrip(" ")
			if self.bib_numbering:
				try:
					if not "episode" in self.bib_numbering.lower() and not "ep" in self.bib_numbering.lower() and not self.bib_numbering.lower().startswith("e") and not "podcast" in self.bib_numbering.lower():# and not self.bib_numbering.lower().startswith("E"):
						self.bib_numbering = "Episode " + self.bib_numbering
				except:
					self.bib_numbering=None


		if self.podcast_name in ["76 small rooms", "Dirt Church Radio"]:
			if "-" in self.episode_title:
				self.bib_title = "-".join(self.episode_title.split("-")[1:]).lstrip(" ")
				self.bib_numbering = "Episode " +self.episode_title.split("-")[0].rstrip(" ")


		if self.podcast_name in ["History of Aotearoa New Zealand podcast"]:
			if "-" in self.episode_title:
				self.bib_title = "-".join(self.episode_title.split("-")[1:]).lstrip(" ")
				self.bib_numbering = self.episode_title.split("-")[0].rstrip(" ")
			if not self.bib_numbering and self.epis_numb:
				self.bib_numbering = "Episode " + self.epis_numb
			
			

		if self.podcast_name in ["The real pod" ,  "The fold"]:
			if ":" in self.episode_title:
				self.bib_title = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")

			
		if self.podcast_name in ["Better off read"]:
			if "Ep " in self.episode_title or "Episode" in self.episode_title:
					self.bib_title = " ".join(self.episode_title.split(" ")[2:])
					self.bib_numbering = " ".join(self.episode_title.split(" ")[:2]).rstrip(":")

		if self.podcast_name in ["The Angus Dunn"]:
			if "The Angus Dunn Podcast " in my_alma.xml_response_data:
				self.bib_title = my_rec["245"]["a"].lstrip("The Angus Dunn Podcast ")
				if "-" in self.bib_title:
					divider = "-"
				if ":" in self.bib_title:
					divider = ":"
				self.bib_numbering =self.bib_title.split(divider)[0]
				
				
		if self.podcast_name in ["Business is boring"]:
			if "Business is boring" in self.episode_title:
				self.bib_title = self.episode_title.lstrip("Business is boring").lstrip(" ").lstrip(":").lstrip(" ")
			if "Business is Boring" in self.episode_title:
				self.bib_title = self.episode_title.lstrip("Business is Boring").lstrip(" ").lstrip(":").lstrip(" ")


		if self.podcast_name in ["TOA Tabletop"]:
			if ":" in self.episode_title:
				if self.episode_title.split(":")[0].isdigit():
					self.bib_title = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
					self.bib_numbering = self.episode_title.split(":")[0].rstrip(' ')

		if self.podcast_name in ["Stag roar"]:
			if ":" in self.episode_title:
				if  not (len(self.episode_title.split(":")[-1].rstrip().lstrip())==4 and self.episode_title.split(":")[-1].rstrip().lstrip().isdigit()):

					self.bib_title = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
					self.bib_numbering = self.episode_title.split(":")[0].rstrip(' ')
			elif '-' in self.episode_title:
				self.bib_title = "-".join(self.episode_title.split("-")[1:]).lstrip(" ")
				self.bib_numbering = self.episode_title.split("-")[0].rstrip(' ')

		if self.podcast_name  in ["NZ everyday investor"]:
			pattern = re.compile(r"(Ep\s*\d+)")
			self.bib_title, self.bib_numbering = self.extract_episode_info(self.episode_title, pattern)

		if self.podcast_name in ["Dr. Tennant's verbal highs"]:
			if ":" in self.episode_title:
				self.bib_title = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
				self.bib_numbering = self.episode_title.split(":")[0].rstrip(' ')

		if self.podcast_name in ["Girls on top"]:
			if "-" in  self.episode_title and self.episode_title.startswith("Episode"):
				self.bib_title = "-".join(self.episode_title.split("-")[1:]).lstrip(" ")
				self.bib_numbering = self.episode_title.split("-")[0].rstrip(' ')
		
		if self.podcast_name in ["Untamed Aotearoa"]:
			if "#" in  self.episode_title:
				self.bib_title = "#".join(self.episode_title.split("#")[1:]).lstrip(" ")
				self.bib_numbering = "# "+ self.episode_title.split("#")[0].rstrip(' ')

		if self.podcast_name in ["B better podcast"]:
			if self.episode_title.startswith("#"):
				self.bib_title = " ".join(self.episode_title.split(" ")[1:]).lstrip(" ")
				self.bib_numbering = self.episode_title.split(" ")[0]


		if self.podcast_name in ["NUKU 100"]:
			if self.episode_title.startswith("//"):
				self.bib_title = " ".join(self.episode_title.split(" ")[1:]).lstrip(" ")
				self.bib_numbering = "Episode "+self.episode_title.split(" ")[0].lstrip("//")
			
		if self.podcast_name in ["NZ tech podcast with Paul Spain"]:
			if  ":" in self.episode_title and ("NZ Tech Podcast" in self.episode_title or "Episode" in self.episode_title) and not "Running time" in self.episode_title:
				ep_number = None
				if ": NZ Tech Podcast" in self.episode_title:
					self.bib_title =  ":".join(self.episode_title.split(":")[:-1])
					ep_number = re.findall(r'[0-9]+', self.episode_title.split(":")[-1])[0]
				elif "NZ Tech Podcast" in self.episode_title:
					self.bib_title = ":".join(self.episode_title.split(":")[1:])
					try:
						ep_number = re.findall(r'[0-9]+', self.episode_title.split(":")[0])[0]
					except:
						logger.info("no episode number")
				elif ": Episode"	 in self.episode_title:
					ep_number = re.findall(r'[0-9]+', self.episode_title.split(":")[1])[0]
				elif self.episode_title.startswith("Episode"):
					ep_number = re.findall(r'[0-9]+', self.episode_title.split(":")[0])[0]

			elif "- NZ Tech Podcast" in self.episode_title:
					self.bib_title =  "-".join(self.episode_title.split(":")[:-1])
	
	

		if self.podcast_name in ["Stirring the pot", "UC science radio"]:
			self.bib_title = str(self.episode_title)
			if self.epis_numb:
				self.bib_title = self.episode_title.strip(self.epis_numb).rstrip(" ").lstrip(" ")
				if self.epis_seas:
					self.bib_numbering = "S{}:E{}".format(self.epis_seas, self.epis_numb)
				else:
					self.bib_numbering ="Episode " +  self.epis_numb
		if self.podcast_name in ["Queenstown life", "Windows on dementia"]:
			self.bib_numbering ="Episode " +  self.epis_numb


		if self.podcast_name == "Chris and Sam podcast":
			self.bib_title = self.episode_title.split(" | ")[0]
			if  " | EP" in self.episode_title:
				self.bib_numbering = "EP"+self.episode_title.split("EP")[1].split(" ")[0]
			elif "EP" in self.episode_title:
				self.bib_title = self.episode_title.split("EP")[0]
				if " - " in self.episode_title:
					self.bib_numbering="EP" + self.episode_title.split("EP")[1].split(" - ")[0]
		if self.podcast_name in  ["Dont give up your day job"]:
			self.bib_title  = " ".join(self.episode_title.split(" ")[1:])
			self.bib_numbering = "Episode " + self.episode_title.split(" ")[0].rstrip(".")
		if self.podcast_name in ["thehappy$aver.com."]:
			if "." and self.episode_title and self.episode_title.split(".")[0].isdigit():
				self.bib_title =".".join(self.episode_title.split(".")[1:]).lstrip(" ")
				self.bib_numbering ="Episode "+self.episode_title.split('.')[0]


		if not self.bib_title:
			self.bib_title = str(self.episode_title)

		dot_or_something = "."

		if self.bib_title.startswith(dot_or_something):
			self.bib_title = self.bib_title.lstrip(dot_or_something).lstrip(" ")
		if self.bib_title.rstrip(" ").endswith("?") or self.bib_title.rstrip(" ").endswith("!") or self.bib_title.rstrip(" ").endswith("."):
			dot_or_something = ""

		self.bib_title = self.bib_title + dot_or_something
		if self.bib_numbering:
			self.bib_numbering = self.bib_numbering + "."

	
	def episode_sprsh_check(self, cell_range):

		"""
		Checking if this title already in spreadsheet
		Returns:
			(bool) - True if title exists or False if the title does not exist in the spreadsheet.

		"""
		for row in cell_range:
			if row.value == self.episode_title:
				#the title exists
				return True #
		return False

	

	def find_description_with_podcastparser(self):
		"""
		Finds description using podcastparser module
		"""
		
		try:
			parsed = podcastparser.parse( self.podcast_url, urlopen(self.rss_filename))
			#for lists of lists all the episode metadata
			for el in parsed:
				main_list = []
				if el == "episodes":
					for elem in parsed['episodes']:
						ep_title = elem["title"]				
						if ep_title == self.episode_title:
								description_html = elem["description_html"]
								self.description2 = re.findall(r'<p>(.*?)</p>', description_html)[0]
								if self.description2.startswith("<iframe"):
									self.description2 = None

		except Exception as e:
			logger.info("could not find with podcastparser")
			logger.info(str(e))
			logger.info(type(e))
			self.description = None
	
	def find_download_link_with_podcastparser(self):
		"""finds mp3 link with podcastparser"""
		
		parsed = podcastparser.parse( self.podcast_url, urlopen(self.rss_filename))
		#print(len(parsed["episodes"]))
		for el in parsed["episodes"]:
			if el["enclosures"]!=[]:
				if el["title"]== self.episode_title:
					self.episode_download_link=el["enclosures"][0]["url"]
					return self.episode_download_link

	def reverse_episodes(self, episodes):
	    

		date1 = episodes[0]["published"]
		date2 = episodes[1]["published"]
		par_date1 = dateparser.parse(date1)
		par_date2 = dateparser.parse(date2)
		if "+" in str(par_date1):
			par_date_end1 = str(par_date1).split("+")[-1]
			par_date_end2 = str(par_date2).split("+")[-1]
			sign = "+"
		else:
			par_date_end1 = str(par_date1).split("-")[-1]
			par_date_end2 = str(par_date2).split("-")[-1]
			sign = "-"
		my_time1 = mktime(datetime.strptime(str(par_date1), f"%Y-%m-%d %H:%M:%S{sign}{par_date_end1}").timetuple())
		my_time2 = mktime(datetime.strptime(str(par_date2), f"%Y-%m-%d %H:%M:%S{sign}{par_date_end2}").timetuple())

		if my_time1<my_time2:
			print ("Ascending order - reversing")

			episodes =  self.reverse_list(episodes)

		else:
			print("Descending order")
		return episodes


	def reverse_list(self, input_list):

		return input_list[::-1]


	def clean_description(self, description):

		"""the script is taking description and cleaning it from tags and special characters
		Args:
			description (str) - episode description from the feed.
		Returns:
			description (str) - cleaned description.

		"""

		# Replace <br/> tags with spaces
		description = description.replace(r"<br/>", " ")

		# Parse the description with BeautifulSoup
		soup = bs(description, "lxml")

		# Replace <p> tags with spaces and remove HTML tags
		for p in soup.find_all('p'):
		    p.insert_after(' ')
		    p.unwrap()

		# Convert the cleaned soup object back to a string
		description = soup.get_text()
		# Further clean the description
		description = description.replace(r"\n", " ").replace(r"\'s", 's').replace("  "," ")
		description = description.rstrip(" ").lstrip("!").replace("–", "-").replace("’", "'").replace("‘","").replace('”', '"').replace('“', '"').replace("—","-")
		#this line removes emoji
		self.description = re.sub('[(\U0001F600-\U0001F92F|\U0001F300-\U0001F5FF|\U0001F680-\U0001F6FF|\U0001F190-\U0001F1FF|\U00002702-\U000027B0|\U0001F926-\U0001FA9F|\u200d|\u2640-\u2642|\u2600-\u2B55|\u23cf|\u23e9|\u231a|\ufe0f)]+','',self.description)

		return description

																					
	def parsing_with_feedparser(self):
		"""
		    Parses podcast feeds, extracts metadata, downloads episodes, and manages database records.

		    This function performs the following tasks:
		    1. Checks if the podcast title matches the expected title.
		    2. Parses the feed using feedparser.
		    3. Iterates through episodes in the feed.
		    4. Checks the episode's publication date and filters episodes based on date.
		    5. Extracts episode metadata such as title, description, tags, links, and download link.
		    6. Downloads episodes using the Downloader class.
		    7. Handles database record management for episodes and files.
		    8. Appends episode information to a Google Sheets spreadsheet.


		    Args:
		        self: An instance of the Harvester class.

		    Returns:
		        None
		"""
		print("PODCAST data from dictionary:")
		for pdcel in self.podcast_data:
			print(pdcel, self.podcast_data[pdcel])
		podcast_name_flag = False
		self.episode_download_link = None
		my_flag = False
		stop_episode_flag = False
		######USE this list for adding backlogs#############################
		#my_list = ["The Aramoana Massacre (PART I)", "Parker-Hulme Murder (Part 2)"]
		###################################################################

		d = feedparser.parse(self.podcast_data["rss_filename"])
		if d["entries"]!=[]:
			episodes = self.reverse_episodes(d["entries"])
			d["entries"] = episodes
		try:
			parsed_title = d["feed"]["title"].rstrip(" ").strip("'")
			podcast_name_flag = True
		except:
			try:
				podc_d = podcastparser.parse(self.podcast_data["rss_filename"], self.podcast_data["url"])
				parsed_title = podc_d["title"].rstrip(" ").strip("'")
				podcast_name_flag = True
			except Exception as e:
				print(str(e))
		if podcast_name_flag:
			print(parsed_title)
			if parsed_title.lower() != podcasts_dict[self.podcast_name]["parsed_title"].lower():
					print(parsed_title.lower())
					#print(self.podcast_name)
					print(podcasts_dict[self.podcast_name]["parsed_title"].lower())
					print("Check podcast title might changed!!!")
					quit()
			#logger.setLevel("DEBUG")
			logger.debug(d)
			for ind in range(len(d["entries"])):

				my_flag = False
				
				self.epis_numb = None
				self.bib_title = None
				self.bib_numbering = None
				self.description = None
				self.description2 = None
				self.epis_seas = None
				self.tags = None
				self.description = None
				self.time_flag= False
				self.download_flag = False
				self.tags_list = ""	
				self.link_dict = {}	
				self.episode_download_link = None
				self.episode_link = None
				self.url = None
				self.f_path = None
				self.file_dictionary = None
				self.flag_for_epis_table = False
				self.flag_for_file = False
				self.spreadsheet_message = ""
				ep_flag = False #use it for backlogs with difficul episodes

				try:
				#parses the date into a timestamp
					self.episode_date = d["entries"][ind]["published"]
					#logger.info(self.episode_date)
					try:

						self.episode_date = mktime(dt.strptime(self.episode_date,"%a, %d %b %Y %H:%M:%S %z").timetuple())

					except:
						try:
							self.episode_date = mktime(dt.strptime(self.episode_date,"%a, %d %b %Y %H:%M:%S GMT").timetuple())
						except:
							try:
								self.episode_date = mktime(dt.strptime(self.episode_date,"%a, %d %b %Y %H:%M:%S +1300").timetuple())
							except:
								try:
									self.episode_date = mktime(dt.strptime(self.episode_date,"%a, %d %b %Y %H:%M:%S +0000").timetuple())
								except:
									self.episode_date = mktime(dt.strptime(self.episode_date,"%a, %d %b %Y").timetuple())
								
									
				#compares the date with the date with the last issue and takes a bigger timestamp - all issues after the last issue

					max_time =  float(self.last_issue)
					if float(int(self.episode_date)) > max_time:
						logger.debug("A new episode")
						self.time_flag = True
					else: 
						stop_episode_flag = True


				except Exception as e:
					logger.error("CANNOT PARSE DATE" + str(e))


				self.episode_title  = re.sub('[(\U0001F600-\U0001F92F|\U0001F300-\U0001F5FF|\U0001F680-\U0001F6FF|\U0001F190-\U0001F1FF|\U00002702-\U000027B0|\U0001F926-\U0001FA9F|\u200d|\u2640-\u2642|\u2600-\u2B55|\u23cf|\u23e9|\u231a|\ufe0f)]+','',d["entries"][ind]["title"]).rstrip(" ")	
				
				#########################################################################################

				#self.time_flag=True
				#######################################################################################################3
				if self.time_flag and not stop_episode_flag:
					logger.debug(self.episode_title)
					try:
						self.episode_link = d["entries"][ind]["link"]
					except:
						pass
					logger.debug(self.episode_link)


					######################USE THIS CONDITION  FOR BACKLOGS##################################3
					if self.podcast_name: #in ["Love this podcast"]:
						my_flag = True
					# for el in my_list:
					# 	if el in self.episode_title:
					# 		my_flag = True
					#########################################################################################



				if my_flag:

						logger.debug(d["entries"][ind]["links"])
				#finds episode link and episode download links 
						try:
							link_dict = d["entries"][ind]["links"]

							for el in link_dict:
								if not "length" in el.keys():
									# print("no length in links - taking episode link")
									if el["type"] == 'text/html':
										if not self.episode_link:
											self.episode_link = el["href"]
								else:
									if el["type"] == "audio/mpeg" or el["type"] == "audio/x-m4a" or el["type"] == "":
										self.episode_download_link = el["href"]
							if not self.episode_download_link:
								try:
									self.find_download_link_with_podcastparser()
								except Exception as e:
									logger.error("Podcastparser could not find episode link")
									logger.error(str(e))
							if self.episode_download_link:
								logger.debug("episode download link "+self.episode_download_link)
						except Exception as e:
							logger.error(str(e))

		
				######################################################################Some rools for links for different podcasts##########################################################################################
						if self.podcast_name in ["Taxpayer talk","Board matters"] and not self.episode_link:
							self.episode_link = self.episode_download_link.split(".mp3")[0]
						if self.podcast_name in ["Dont give up your day job","Kiwi birth tales"]:
							self.episode_link = self.podcast_url
						
				############################################################################################################################################################################################################
						
						try:	
								tags_list = ""
								tags = d["entries"][ind]["tags"]
								for  idx in range(len(tags)):
									tags_list+= tags[idx]["term"]
									tags_list += ", "
								self.tags_list = tags_list.rstrip(', ')

						except Exception as e:
							logger.debug(str(e))
							logger.debug("could not find tags")

						if not self.description:
							try:
								self.description =  d["entries"][ind]["summary_detail"]["value"]

								if "[&#8230;]" in self.description:							
									self.description = d["entries"][ind]["content"][0]["value"]
							except KeyError:
								logger.error("could not get description by summary details")
							except Exception as e:
								logger.error(str(e))

						if not self.description:
							try:
								logger.debug("podcastparser description")
								self.find_description_with_podcastparser()
								self.description = self.description2
							except Exception as e:
								logger.error(str(e))

						if not self.description:
							logger.error("!!!No description!!!")
							
				#############################################################Here could be rools for different podcast titles############################################
						if self.podcast_name in ["Human-robot interaction podcast"]:
							self.find_description_with_podcastparser()
							if self.description2:
								self.description = self.description+" "+ self.description2
				#########################################################################################################################################################
						try:
							self.epis_numb =  d["entries"][ind]["itunes_episode"]
						except:
							pass
						try:
							self.epis_seas = d["entries"][ind]['itunes_season']
						except:
							pass

						print(self.episode_download_link)

						if self.episode_download_link:
							self.download_flag = True
						if self.download_flag:				
							flag_for_epis_table = True
							flag_for_file = False
							self.f_path = os.path.join(file_folder, self.podcast_name.strip('’'))
							if ":" in self.podcast_name:
								self.f_path =os.path.join(file_folder, self.podcast_name.split(":")[0].strip("’").rstrip(" "))
							if "/" in self.podcast_name:
								self.f_path =os.path.join(file_folder, self.podcast_name.split("/")[0].strip("’").rstrip(" "))
							if "." in self.podcast_name:
								self.f_path =os.path.join(file_folder, self.podcast_name.strip(".").rstrip(" "))

							if not os.path.isdir(self.f_path):
								os.mkdir(os.path.join(self.f_path))

							#calls downloader module
							print("Calling downloader_light_modified.")

							downloader = Downloader(self.episode_download_link, self.f_path, collect_html=False, proxies=None)
							print("Message from downloader:")
							logger.info(downloader.message)
							
							if downloader.size_original == 0:
								logger.info("There is empty file on {} in {} of {}. Please contact publisher".format(episode_download_link, episode_title, podcast_name))
								self.spreadsheet_message = "!!!D Not Tick. Empty file. Ask pusblisher!!!"

							if not downloader.download_status  or (downloader.filesize == 0 and downloader.size_original != 0) or (downloader.download_status and downloader.message and "Content-Disposition" in downloader.message):# or (downloader.filesize == 0 and downloader.size_original != 0):# or not self.jhove_check(downloader.filepath)

							# if not downloader.download_status  or (downloader.filesize == 0 and downloader.size_original != 0):

								downloader = Downloader(self.episode_download_link, self.f_path, collect_html=False, proxies=None)
								if not downloader.download_status:
									with open("skipped_episode_check_please.txt","a") as f:
										f.write("{}|{}|{}|{}|{}".format(self.podcast_name, self.episode_title, self.episode_link, self.episode_download_link, downloader.message))
										f.write("\n")
								# elif not downloader.jhove_check(downloader.filepath):
								# 	logger.error("File is not well-formed")
								# 	quit()
							print("Status:")
							print(downloader.download_status)
							if downloader.download_status:

								if downloader.filename_from_headers or downloader.filename_from_url:
										if downloader.filename_from_headers and downloader.filename_from_headers != "media.mp3" and len(downloader.filename_from_headers)<70 and not "%" in downloader.filename_from_headers:									
											if self.check_for_meaning(downloader.filename_from_headers):
												downloader.change_filename(rename_from_headers = True)
												logger.debug("filename from headers " + downloader.filename_from_headers)
										elif downloader.filename_from_url and downloader.filename_from_url != "media.mp3" and len(downloader.filename_from_url)<70 and not "%" in downloader.filename_from_url:
											logger.debug("file name from url "+downloader.filename_from_url)
											if self.check_for_meaning(downloader.filename_from_url):
												downloader.change_filename(rename_from_url = True)
										if downloader.exists:
											downloader.filepath = downloader.new_filepath
											downloader.filename = downloader.new_filename
								print("Message from downloader:")
								print(downloader.message)			
								if not downloader.message or (downloader.message and 'Content-D' in downloader.message): #self.podcast_name in ["Kiwi birth tales", "Board matters","Advanced analytics","Dirt Church Radio","Chris and Sam podcast"]):
									my_podcast = DbHandler()
									episode_dict = my_podcast.db_reader(["episode_title"],[self.podcast_name],True)

									#checks if episode title in db
									for epsd in episode_dict:
										if not epsd == {}:
											if epsd["episode_title"] == self.episode_title:
												logger.info(f"the episode {self.episode_title} is in db")
												self.flag_for_epis_table = True

									#checks if filepath in db
									try:
										file_dict = my_podcast.db_reader(["filepath"], [self.podcast_name], True)
										for flpth in file_dict:
											if not flpth =={}:
												if flpth["filepath"] == downloader.filepath:
													self.flag_for_file = True
													logger.info(f"the file {downloader.filepath} exists")
									except KeyError as e:
										logger.debug(str(e))
										

									##################################### Cleaning part###############################################################################################################
									#cleans epiosode title and description
									self.split_rss_title()
									self.episode_title = self.episode_title.rstrip(" ").lstrip("!").replace("–", "-").replace("’", "'").replace("‘","").replace('”', '"').replace('“', '"').replace("—","-")
									if self.spreadsheet_message !="":
										self.episode_title == self.spreadsheet_message + self.episode_title
									if not self.description:
										self.description = ""

									self.description = self.clean_description(self.description)
									if  self.description.endswith("."):
										self.description.rstrip(".")

									if not self.episode_link:
										self.episode_link = str(self.episode_download_link)
									self.episode_link = self.episode_link.rstrip(" ")	
									tick = False
									if self.serial_mms in serials:
										tick = True
									if podcasts_dict[self.podcast_name]["automated_flag"] == True:
										tick = True

									#Reading database for title again to avoid duplicates									
									episode_dict2= my_podcast.db_reader(["episode_title"],[self.podcast_name],True)

									#checks if episode title in db
									for epsd in episode_dict2:
										if not epsd == {}:
											if epsd["episode_title"] == self.episode_title:
												logger.info(f"the episode {self.episode_title} is in db")
												self.flag_for_epis_table = True
									if not self.flag_for_epis_table:

										logger.info("this episode is not in db")

										episode_data = {"podcast": self.podcast_id,"episode_title":self.episode_title, "bib_title":self.bib_title, "bib_numbering":self.bib_numbering, "description":self.description, "date_harvested":downloader.datetime, "date":self.episode_date, "harvest_link": self.episode_download_link, "episode_link":self.episode_link, "epis_numb" : self.epis_numb, "epis_seas" : self.epis_seas, "tick" : tick}
										my_podcast.table_creator("Episode", episode_data)
										episode = my_podcast.my_id.id
										#print(episode)
										logger.info("Episode data added to db")
										self.flag_for_epis_table = True
									try:
										file_dict = my_podcast.db_reader(["filepath"], [self.podcast_name], True)
										for flpth in file_dict:
											if not flpth =={}:
												if flpth["filepath"] == downloader.filepath:
													self.flag_for_file = True
													logger.info(f"the file {downloader.filepath} exists")


									except KeyError as e:
										logger.debug(str(e))


									if self.flag_for_epis_table:

										id_dict = my_podcast.db_reader(["episode_id","episode_title"],[self.podcast_name],True)
										for el in id_dict:
											print(self.episode_title)
											if el["episode_title"] == self.episode_title:
												episode =  el["episode_id"]
										

										file_data = {"episode" : episode, "filepath" : downloader.filepath, "md5sum" : downloader.md5, "md5_from_file" : downloader.md5_original, "filesize" : downloader.filesize, "size_original" : downloader.size_original, "file_type" : downloader.filetype_extension}	
										if not self.flag_for_file:
											logger.info("This file is not in db")
											if not my_podcast.db_if_file_for_episode_id(self.podcast_name, episode):
												my_podcast.table_creator("File", file_data)
												logger.info("File added to db")
											else:
												logger.info("This episode has a file")
												my_podcast.file_updator(episode, file_data)
												logger.info("DB updated with a new file info")

									# print(self.episode_sprsh_check())
									if not self.episode_sprsh_check(self.cell_range) and not tick:
											connection_count = 0
											while not connection_count >= 5:
												connection_count +=1
												try:

													print([
													    self.podcast_name,
													    podcasts_dict[self.podcast_name]["serial_mms"],
													    podcasts_dict[self.podcast_name]["rss_filename"],
													    self.episode_title,
													    self.bib_title,
													    self.bib_numbering,
													    self.epis_seas,
													    self.epis_numb,
													    self.description,
													    self.episode_link,
													    dt.fromtimestamp(int(self.episode_date)).strftime('%B %d %Y'),
													    self.tags_list,
													    self.episode_download_link,
													    downloader.datetime.strftime('%B %d %Y')
													])
													ws.append_row([self.podcast_name, podcasts_dict[self.podcast_name]["serial_mms"], podcasts_dict[self.podcast_name]["rss_filename"], self.episode_title, self.bib_title, self.bib_numbering, self.epis_seas, self.epis_numb, self.description, self.episode_link, dt.fromtimestamp(int(self.episode_date)).strftime('%B %d %Y'), self.tags_list, self.episode_download_link, downloader.datetime.strftime('%B %d %Y')])
													logger.info("a new row appended to the spreadsheet")
													break

												except gspread.exceptions.APIError as e:
													logger.error(str(e))
													sleep(10)
							else:
								quit()
								



	def check_for_meaning(self, my_filename):

		"""Checks filename for possible meaningful words
		Parameters:
			my_filename (str) - filename to check
		Returns:
			word_meaning_flag(bool) - set True if meaningful word found
		"""
		word_meaning_flag = False
		lst1  = []
		lst2 = []
		lst3=[]
		logger.debug(f"Checking for meaning {my_filename}")
		if "." in my_filename:
			my_filename = my_filename.split(".")[0]
		if "-" in my_filename:
			lst1 = my_filename.split("-")
		if "_" in my_filename:
			lst2=my_filename.split("_")
		if '+' in my_filename:
			lst3 = my_filename.split('+')
		lst = lst1+lst2+lst3
		for el in lst:
			if el.lower() in words.words():
				word_meaning_flag = True
		return word_meaning_flag


	def harvester(self):

		""" 
		    Collects files and metadata for all the issues after the last issue  of podcasts listed in dictionary. 	    

	    Args:
			podcast_name (str): podcast name
			podcast_data (dict): one record from podcasts_dict which contains information of one podcast						
	    Returns:
	        None

	    """

		self.download_flag = False
		self.flag_for_podc_table = True
		self.rss_filename = self.podcast_data["rss_filename"]
		url = self.podcast_data["url"]
		self.parsing_with_feedparser()

	

def harvest():
	"""
	Checks if podcast name in db. Creates if not. Runs harvester
	"""
	harvest_flag = False
	flag_last_name = False
	second_last_flag = False
	final_flag = False
	my_podcast_name = list(podcasts_dict.keys())[0]

	ws = gs.get_worksheet(0)
	# try:
	for i, podcast_name in enumerate(podcasts_dict):


		if list(podcasts_dict.keys())[i] == my_podcast_name:
			harvest_flag = True
		if podcast_name == list(podcasts_dict.keys())[-1]:
			if flag_last_name:
				second_last_flag = True
			flag_last_name = True
	
		if harvest_flag and not second_last_flag:
			flag_for_podc_table = False
			logger.info("*"*50)
			logger.info(podcast_name)
			logger.info("*"*50)

			my_podcast = DbHandler()
			name_dict = my_podcast.db_reader(["podcast_id", "last_issue"],[podcast_name],True)
			if name_dict != []:
				flag_for_podc_table = True
				last_issue = name_dict[0]["last_issue"]
				podcast_id = name_dict[0]["podcast_id"]
			if not flag_for_podc_table:
				my_podcast.table_creator("Podcast",{"podcast_name":podcast_name,"serial_mms":podcasts_dict[podcast_name]["serial_mms"], "serial_pol":podcasts_dict[podcast_name]["serial_pol"],"rss_filename":podcasts_dict[podcast_name]["rss_filename"],"publish_link_ro_record":podcasts_dict[podcast_name]["publish_link_ro_record"],"automated_flag":podcasts_dict[podcast_name]["automated_flag"],"access_policy":podcasts_dict[podcast_name]["access_policy"], "location":podcasts_dict[podcast_name]["url"], "template_name":podcasts_dict[podcast_name]["template_name"]})
				logger.info("Podcast table for {} created. ID - {}".format(podcast_name, my_podcast.my_id))
				podcast_id = my_podcast.my_id
				last_issue = 0

			my_episode = Harvester(podcast_id, podcast_name, podcasts_dict[podcast_name], last_issue, podcasts_dict[podcast_name]["url"] ,podcasts_dict[podcast_name]["serial_mms"])
			my_episode.cell_range = my_episode.reload_spreadsheet()
			my_episode.harvester()

			final_flag = True
		
	if not final_flag:
		quit()

	
						



def main():
	harvest()

if __name__ == "__main__":
	main()
