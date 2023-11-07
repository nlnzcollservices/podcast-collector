import os
import sys
import re
import feedparser
import podcastparser
import subprocess
import gspread
sys.path.insert(0, r'H:\GIT\file-downloader')
from downloader_light_modified import DownloadResource as Downloader
sys.path.insert(0, r"Y:\ndha\pre-deposit_prod\LD_working\alma_tools")
from alma_tools import AlmaTools
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from time import time, sleep, mktime
from datetime import datetime as dt
from podcast_dict import podcasts_dict, serials
from database_handler import DbHandler
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
try:
	from settings import  file_folder, report_folder, podcast_sprsh, logging,creds #!!!! report
except:
	from settings_prod import  file_folder, report_folder, podcast_sprsh, logging,creds
logger = logging.getLogger(__name__)

#######################################Creating google spreadsheet object#################################################


c = gspread.authorize(creds)
gs = c.open_by_key(podcast_sprsh)
#change if the name or id of the worksheet is different
ws = gs.get_worksheet(0)


def reload_spreadsheet():

		c = gspread.authorize(creds)
		gs = c.open_by_key(podcast_sprsh)
		ws = gs.get_worksheet(0)
		rng = "D2:D{}".format(ws.row_count)	
		cell_range = ws.range(rng)
		return cell_range
	
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

	# def reload_spreadsheet(self, function, parameters):

	# 	"""
	# 	Reload the google spreadsheet
	# 	Parameters:
	# 		function (def) - any function to be reloaded with new ws
	# 		parameters (list) - parameters to path there
	# 	"""

	# 	store = file.Storage(client_secrets_file)
	# 	creds = store.get()
	# 	c = gspread.authorize(creds)
	# 	gs = c.open_by_key(podcast_sprsh)
	# 	ws = gs.get_worksheet(0)
	# 	function(ws, parameters)




	# def episode_sprsh_check(self):

	# 	"""
	# 	Checking if this title already in spreadsheet
	# 	Returns:
	# 		(bool) - True if title exists or False if the title does not exist in the spreadsheet.

	# 	"""

	# 	logger.info("Checking {} in the spreadsheet".format(self.episode_title))
	# 	rng = "D2:D{}".format(ws.row_count)	
	# 	try:
	# 		cell_range = ws.range(rng)
	# 		logger.info("cell range found")
	# 	except gspread.exceptions.APIError as e:
	# 		logger.debug(str(e))
	# 		sleep(10)
	# 		self.reload_spreadsheet(self.episode_sprsh_check, None)
	# 		cell_range = ws.range(rng)
	# 	for row in cell_range:
	# 		if row.value == self.episode_title:
	# 			#the title exists
	# 			return True #
	# 	return False


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

	# def jhove_check(self, filepath):

	# 	"""Checks if the file well-formed valid:
	# 	Arguments:
	# 		filepath(str) - file to the pass to check
	# 	Returns:
	# 		(bool) - true if file is good and False in other case"""

	# 	command = [r'jhove',filepath,'-t', 'text'] # the shell command
	# 	process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	# 	output, error = process.communicate()
	# 	output = str(output).split(r"\r\n")[1:-1]
	# 	for el in output:
	# 		if 'Status' in el:
	# 			if "Well-Formed and valid" in el:
	# 				return True
	# 	return False



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
					self.episode_download_link=enclosure["url"]


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
		# except:
		# 	my_time1 = mktime(datetime.strptime(str(par_date1), "%Y-%m-%d %H:%M:%S+00:00").timetuple())
		# 	my_time2 = mktime(datetime.strptime(str(par_date2), "%Y-%m-%d %H:%M:%S+00:00").timetuple())
		print(my_time1)
		print(my_time2)
		if my_time1<my_time2:
			print ("Ascending!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			print(episodes)
			episodes =  self.reverse_list(episodes)
			print("herr1")
			print(episodes)
		else:
			print("Descending@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
		return episodes


	def reverse_list(self, input_list):
		return input_list[::-1]

																					
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

		    Note:
		    - This function contains a mix of tasks, consider breaking them into separate functions for clarity.
		    - Error handling for various cases is included in the code.

		    Args:
		        self: An instance of the Harvester class.

		    Returns:
		        None
		"""
		podcast_name_flag = False
		self.episode_download_link = None
		my_flag = False
		stop_episode_flag = False
		######USE this list for adding backlogs#############################
		#my_list = ["The Aramoana Massacre (PART I)", "Parker-Hulme Murder (Part 2)"]
		###################################################################
		d = feedparser.parse(self.podcast_data["rss_filename"])
		if d["entries"]!=[]:
			print(d["entries"])
			episodes = self.reverse_episodes(d["entries"])
			print(episodes)
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
					print(parsed_title)
					print(self.podcast_name)
					print("Check podcast title might changed!!!")
					quit()
			#logger.setLevel("DEBUG")
			logger.debug(d)
			for ind in range(len(d["entries"])):
				my_flag = False
				
				self.epis_numb = None
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
				#finds the podcast publishing date
				try:
				#parses the date into a timestamp
					self.episode_date = d["entries"][ind]["published"]
					# print(self.episode_date)
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
					# if self.podcast_name =="Front page":
					# 	if float(int(self.episode_date)) > max_time and   float(int(self.episode_date)) < 1540724400.0:
					# 		logger.debug("A new episode")
					# 		self.time_flag = True	
					if float(int(self.episode_date)) > max_time:
						logger.debug("A new episode")
						self.time_flag = True
					else: 
						stop_episode_flag = True


				except Exception as e:
					logger.error("CANNOT PARSE DATE" + str(e))


				self.episode_title  = re.sub('[(\U0001F600-\U0001F92F|\U0001F300-\U0001F5FF|\U0001F680-\U0001F6FF|\U0001F190-\U0001F1FF|\U00002702-\U000027B0|\U0001F926-\U0001FA9F|\u200d|\u2640-\u2642|\u2600-\u2B55|\u23cf|\u23e9|\u231a|\ufe0f)]+','',d["entries"][ind]["title"]).rstrip(" ")	
				##### use this part to harvest backlogs######################################################
				# if self.episode_date < 1397131200.0: 
				# 	self.time_flag = True
				# else:
				# 	self.time_flag = False
				# if "259" in self.episode_title is self.episode_title:
				# 	ep_flag = True
				###################################USE THIS  for LOGS##########################################################
				# if self.podcast_name  == "Shared lunch":
				# # 	if self.episode_title.startswith("The growing impact of"):
				# 	if self.episode_date > 1667397245: 
				# 		self.time_flag = True
				# 	else:
				# 		self.time_flag = False
				# if self.podcast_name == "Property academy":
				# 	if "840k" in self.episode_title:
				# 		self.time_flag = True
				# 	else:
				# 		self.time_flag = False

				# if self.podcast_name == "Access granted":
				# 	if self.episode_date <1491393600.0:
				# 		self.time_flag = True
				# 	else:
				# 		self.time_flag=False
				# if self.podcast_name == "On the rag":
				# 	if "Scrambled brains" in self.episode_title:
				# 		self.time_flag = True
				# 	else:
				# 		self.time_flag = False

				# if "Chris and Sam" in self.podcast_name:
				# 	chris_sam_list = ["Chris Laughing","Indian Scammer Phone Call","Camp Quality","Rated Shackles","Dub FX in the Car"]
				# 	for cse in chris_sam_list:
				# 		if cse in self.episode_title:
				# 			self.time_flag = True

				# if self.podcast_name == "Cult popture":
				# 	cult_pop_list = ["Coming 2 America","Pitching Period Piece Prequels","You Will Never Get This Impossible","Director Trademark Quiz"]
				# 	for cpe in cult_pop_list:
				# 		if cpe in self.episode_title:
				# 			self.time_flag = True

				if self.podcast_name == "B-side stories":
					bs_list = ["Sarah Child & Pip Cameron","New Zealand Society Of Authors 20170523","Joris De Bres on Trees That Count","The 2017 Wellington Jazz Festival preview"]
					for cpe in bs_list:
						if cpe in self.episode_title:
							self.time_flag = True

				# if self.podcast_name == "Hosting":
				# 	if self.episode_date <1481540400.0:
				# 		self.time_flag = True
				# 	else:
				# 		self.time_flag=False
				# if self.podcast_name == "Dietary requirements":
				# 	if self.episode_date <1601463600.0:
				# 		self.time_flag = True
				# 	else:
				# 		self.time_flag=False
				# if self.podcast_name == "Democracy Project":
				# 	dem_proj_list = ['lowering the voting age','Labour tax and dental care policie','Wayne Mapp','Green Party private school controversy']
				# 	for dpe in dem_proj_list:
				# 		if dpe in self.episode_title:
				# 			self.time_flag = True
				# if self.podcast_name == "Advanced analytics":
				# 	if "End of season survey" in self.episode_title:
				# 		self.time_flag = True
				# 	else:
				# 		self.time_flag = False
				# if self.podcast_name == "Stirring the pot":
				# 	if "s Future Forum" in self.episode_title:
				# 		self.time_flag = True
				# 	else:
				# 		self.time_flag = False

				# if self.podcast_name  == "Mud & blood":
				# 	mab_list = ["Mörk Borg Review","Dissident Whispers"]
				# 	for mbe in mab_list:
				# 		if mbe in self.episode_title:
				# 			self.time_flag = True
				# if self.podcast_name == 'The watercooler':
				# 	if self.episode_date >1476529200.0:
				# 		self.time_flag = True
				# 	else:
				# 		self.time_flag=False
				self.time_flag=True
				#######################################################################################################3
				if self.time_flag and not stop_episode_flag:
					logger.info(self.episode_title)
					try:
						self.episode_link = d["entries"][ind]["link"]
					except:
						pass
					logger.info(self.episode_link)
					print(my_flag)
					print(self.episode_title)

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
								logger.info("episode download link "+self.episode_download_link)
						except Exception as e:
							logger.error(str(e))

		
						print(self.episode_link)

				######################################################################Some rools for links for different podcasts##########################################################################################
						if self.podcast_name in ["Taxpayer talk","Board matters"] and not self.episode_link:
							self.episode_link = self.episode_download_link.split(".mp3")[0]
						if self.podcast_name in ["Paige's space","Kelli from the Tron","Top writers radio show", "Dont give up your day job","Motherness","Kiwi birth tales"]:
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
							logger.info(str(e))
							logger.info("could not find tags")

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
							downloader = Downloader(self.episode_download_link, self.f_path, collect_html=False, proxies=None)
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
							print(downloader.download_status)
							if downloader.download_status:

								if downloader.filename_from_headers or downloader.filename_from_url:
										if downloader.filename_from_headers and downloader.filename_from_headers != "media.mp3" and len(downloader.filename_from_headers)<70 and not "%" in downloader.filename_from_headers:									
											if self.check_for_meaning(downloader.filename_from_headers):
												downloader.change_filename(rename_from_headers = True)
												logger.info("filename from headers " + downloader.filename_from_headers)
										elif downloader.filename_from_url and downloader.filename_from_url != "media.mp3" and len(downloader.filename_from_url)<70 and not "%" in downloader.filename_from_url:
											logger.info("file name from url "+downloader.filename_from_url)
											if self.check_for_meaning(downloader.filename_from_url):
												downloader.change_filename(rename_from_url = True)
										if downloader.exists:
											downloader.filepath = downloader.new_filepath
											downloader.filename = downloader.new_filename
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
									print(self.episode_title)
									print(self.description)
									self.episode_title = self.episode_title.rstrip(" ").lstrip("!").replace("–", "-").replace("’", "'").replace("‘","").replace('”', '"').replace('“', '"').replace("—","-")
									if self.spreadsheet_message !="":
										self.episode_title == self.spreadsheet_message + self.episode_title
									if not self.description:
										self.description = ""
									self.description = bs(self.description,"lxml").text
									self.description = self.description.replace(r"\n", " ").replace(r"\'s", 's').replace("  "," ")#.replace("►"," ").
									self.description = self.description.rstrip(" ").lstrip("!").replace("–", "-").replace("’", "'").replace("‘","").replace('”', '"').replace('“', '"').replace("—","-")
									#this line removes emoji
									self.description = re.sub('[(\U0001F600-\U0001F92F|\U0001F300-\U0001F5FF|\U0001F680-\U0001F6FF|\U0001F190-\U0001F1FF|\U00002702-\U000027B0|\U0001F926-\U0001FA9F|\u200d|\u2640-\u2642|\u2600-\u2B55|\u23cf|\u23e9|\u231a|\ufe0f)]+','',self.description)
									logger.debug(self.episode_link)
									if not self.episode_link:
										self.episode_link = str(self.episode_download_link)
									self.episode_link = self.episode_link.rstrip(" ")	
									tick = False
									if self.serial_mms in serials:
										tick = True
									if podcasts_dict[self.podcast_name]["automated_flag"] == True:
										tick = True
									if not self.flag_for_epis_table:

										logger.info("this episode is not in db")

										episode_data = {"podcast": self.podcast_id,"episode_title":self.episode_title, "description":self.description, "date_harvested":downloader.datetime, "date":self.episode_date, "harvest_link": self.episode_download_link, "episode_link":self.episode_link, "epis_numb" : self.epis_numb, "epis_seas" : self.epis_seas, "tick" : tick}
										my_podcast.table_creator("Episode", episode_data)
										episode = my_podcast.my_id.id
										
									if not self.flag_for_file:
										if self.flag_for_epis_table:
											id_dict = my_podcast.db_reader(["episode_id","episode_title"],[self.podcast_name],True)
											for el in id_dict:
												if el["episode_title"] == self.episode_title:
													episode =  el["episode_id"]
				
										logger.info("this file is not in db")

										file_data = {"episode" : episode, "filepath" : downloader.filepath, "md5sum" : downloader.md5, "md5_from_file" : downloader.md5_original, "filesize" : downloader.filesize, "size_original" : downloader.size_original, "file_type" : downloader.filetype_extension}
										my_podcast.table_creator("File", file_data)
									# print(self.episode_sprsh_check())
									if not self.episode_sprsh_check(self.cell_range) and not tick:
										 	connection_count = 0
										 	while not connection_count >= 5:
										 		connection_count +=1
										 		try:
										 			print([self.podcast_name, podcasts_dict[self.podcast_name]["serial_mms"], podcasts_dict[self.podcast_name]["rss_filename"], self.episode_title, self.description, self.episode_link, dt.fromtimestamp(int(self.episode_date)).strftime('%B %d %Y'), self.tags_list, self.episode_download_link])
										 			ws.append_row([self.podcast_name, podcasts_dict[self.podcast_name]["serial_mms"], podcasts_dict[self.podcast_name]["rss_filename"], self.episode_title, self.description, self.episode_link, dt.fromtimestamp(int(self.episode_date)).strftime('%B %d %Y'), self.tags_list, self.episode_download_link])
										 			logger.info("a new row appended")
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
		logger.info(f"Checking for meaning {my_filename}")
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

		print(my_podcast_name)
		print(list(podcasts_dict.keys())[i])

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
			print(name_dict)
			if name_dict != []:
				flag_for_podc_table = True
				last_issue = name_dict[0]["last_issue"]
				podcast_id = name_dict[0]["podcast_id"]
			if not flag_for_podc_table:
				my_podcast.table_creator("Podcast",{"podcast_name":podcast_name,"serial_mms":podcasts_dict[podcast_name]["serial_mms"], "serial_pol":podcasts_dict[podcast_name]["serial_pol"],"rss_filename":podcasts_dict[podcast_name]["rss_filename"],"publish_link_ro_record":podcasts_dict[podcast_name]["publish_link_ro_record"],"automated_flag":podcasts_dict[podcast_name]["automated_flag"],"access_policy":podcasts_dict[podcast_name]["access_policy"], "location":podcasts_dict[podcast_name]["url"], "template_name":podcasts_dict[podcast_name]["template_name"]})
				logger.info("Podcast table for {} created. ID - {}".format(podcast_name, my_podcast.my_id))
				podcast_id = my_podcast.my_id
				last_issue = 0
			# for i in range(3):
			# 	process = True
			# 	if process:
			# try:
			my_episode = Harvester(podcast_id, podcast_name, podcasts_dict[podcast_name], last_issue, podcasts_dict[podcast_name]["url"] ,podcasts_dict[podcast_name]["serial_mms"])
			my_episode.cell_range = reload_spreadsheet()
			my_episode.harvester()
			# 	process = False

			# except Exception as e:
			# 	sleep(10)
			final_flag = True
		# except Exception  as er:
		# 	print(str(er))
		# 	for ind in range(10):
		# 		print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		# 	my_podcast_name = str(podcast_name)
		# 	final_flag = False

		# 	harvest_flag = False
	if not final_flag:
		quit()

	
						



def main():
	harvest()

if __name__ == "__main__":
	main()
