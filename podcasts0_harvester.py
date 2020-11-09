import os
import sys
import feedparser
import podcastparser
import subprocess
import gspread
sys.path.insert(0, r'H:\GIT\file-downloader')
from downloader_light_modified import DownloadResource as Downloader
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from time import time, sleep, mktime
from datetime import datetime as dt
from podcast_dict import podcasts_dict
from database_handler import DbHandler
from nltk.corpus import words
import nltk
nltk.download('words')
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

	
class Harvester():

	"""
		This class manages harvesting podcast episodes via rss feed.

		Attributes
		----------

	    podcast_name(str) - name of podcast from podcasts_dict. Should be the same as in serial_record
	    podcast_data(dict) - dictionary which contains information about particular podcast
	    podcast_id(int) - id of podcast in db


	 	Methods
		-------
		__init__(self, podcast_id, podcast_name, podcast_data, last_issue)
		reload_spreadsheet(self, function, parameters)
		episode_sprsh_check(self)
		jhove_check(self, filepath)
		find_description_with_podcastparser(self)
		parsing_with_feedparser(self)
		check_for_meaning(self, my_filename)
	"""

	def __init__(self, podcast_id, podcast_name, podcast_data, last_issue):
		

		self.podcast_id = podcast_id
		self.podcast_name = podcast_name
		self.podcast_data = podcast_data
		self.last_issue = last_issue
		self.download_flag = False
		self.flag_for_podc_table = True
		self.episode_title = None
		self.episode_sprsh_check = None
		self.url = None
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

	def reload_spreadsheet(self, function, parameters):

		"""
		Reload the google spreadsheet
		Parameters:
			function (def) - any function to be reloaded with new ws
			parameters (list) - parameters to path there
		"""

		store = file.Storage(client_secrets_file)
		creds = store.get()
		c = gspread.authorize(creds)
		gs = c.open_by_key(podcast_sprsh)
		ws = gs.get_worksheet(0)
		function(ws, parameters)

	def episode_sprsh_check(self):

		"""
		Checking if this title already in spreadsheet
		Returns:
			(bool) - True if title exists or False if the title does not exist in the spreadsheet.

		"""
		logger.info("Checking {} in the spreadsheet".format(self.episode_title))
		rng = "D2:D{}".format(ws.row_count)	
		try:
			cell_range = ws.range(rng)
			logger.info("cell range found")
		except gspread.exceptions.APIError as e:
			logger.debug(str(e))
			sleep(10)
			self.reload_spreadsheet(self.episode_sprsh_check, None)
			cell_range = ws.range(rng)
		for row in cell_range:
			if row.value == self.episode_title:
				#the title exists
				return True #
		return False

	def jhove_check(self, filepath):

		"""Checks if the file well-formed valid:
		Arguments:
			filepath(str) - file to the pass to check
		Returns:
			(bool) - True if file is good and False in other case"""

		command = [r'jhove',filepath,'-t', 'text'] # the shell command
		process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		output, error = process.communicate()
		output = str(output).split(r"\r\n")[1:-1]
		for el in output:
			if 'Status' in el:
				if "Well-Formed and valid" in el:
					return True
		return False



	def find_description_with_podcastparser(self):
		"""
		Finds description using podcastparser module
		"""
		
		try:
			parsed = podcastparser.parse( self.url, urlopen(self.rss_filename))
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
	


	def parsing_with_feedparser(self):

		"""
		Parses feeds to extract metadata such as date, title, tags, description, season, number and download_link. 
		Calls downloader to download the file and manages the file name
		Checks if the episode exists in db or file exist in db and creates new record for Episode and File tables
		Checks if the episode title in the spreadsheet and adds the row if not
		"""

		self.episode_download_link = None
		

		d = feedparser.parse(self.podcast_data["rss_filename"])
		logger.debug(d)
		for ind in range(len(d["entries"])):
			self.epis_numb = None
			self.description = None
			self.description2 = None
			self.epis_seas = None
			self.tags = None
			self.description = None
			self.time_flag= False
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
			#finds the podcast publishing date
			try:
			#parses the date into a timestamp
				self.episode_date = d["entries"][ind]["published"]
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
			except Exception as e:
				logger.error("CANNOT PARSE DATE" + str(e))
			self.episode_title  = d["entries"][ind]["title"]	
			if self.time_flag:
				logger.info(self.episode_title)
				try:
					self.episode_link = d["entries"][ind]["link"]
				except:
					pass
				logger.info(self.episode_link)			
				if self.episode_title:# in ["Living the designer's life, while the world watches • Charli Prangley, Design & YouTube superstar", "Creating a feast for the eyes, heart and mind • Natasha Lampard, Co-founder, Webstock","Storytelling with holographic maps • Chris Hay, founder of Locales","Master class in launching a startup • Sonya Williams, co-founder of Sharesies"]:
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
						logger.info("episode download link "+self.episode_download_link)
					except Exception as e:
						logger.error(str(e))
			######################################################################Some rools for links for different podcasts##########################################################################################
					if self.podcast_name in ["Taxpayer talk"] and not self.episode_link:
						self.episode_link = self.episode_download_link.split(".mp3")[0]
					if self.podcast_name in ["Top writers radio show", "Dont give up your day job"]:
						self.episode_link = ""
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
							quit()
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
							self.f_path =os.path.join(file_folder, podcast_name.split(":")[0].strip("’").rstrip(" "))
						if "/" in self.podcast_name:
							self.f_path =os.path.join(file_folder, podcast_name.split("/")[0].strip("’").rstrip(" "))
						if not os.path.isdir(self.f_path):
							os.mkdir(os.path.join(self.f_path))

			#calls downloader module
						downloader = Downloader(self.episode_download_link, self.f_path, collect_html=False, proxies=None)
						logger.info(downloader.message)
						
						if downloader.size_original == 0:
							logger.info("Ther is empty file on {} in {} of {}. Please contact publisher".format(episode_download_link, episode_title, podcast_name))
							self.spreadsheet_message = "!!!D Not Tick. Empty file. Ask piblisher!!!"
						if not downloader.download_status or not self.jhove_check(downloader.filepath) or (downloader.filesize == 0 and downloader.size_original != 0):

						# if not downloader.download_status  or (downloader.filesize == 0 and downloader.size_original != 0):

							downloader = Downloader(self.episode_download_link, self.f_path, collect_html=False, proxies=None)
							if not downloader.download_status:
								downloader.message
							if not self.jhove_check(downloader.filepath):
								logger.error("File is not well-formed")
								quit()



						if downloader.filename_from_headers or downloader.filename_from_url:
							if downloader.filename_from_headers or downloader.filename_from_url:
								if downloader.filename_from_headers and downloader.filename_from_headers != "media.mp3":									
									if self.check_for_meaning(downloader.filename_from_headers):
										downloader.change_filename(rename_from_headers = True)
										logger.info("filename from headers " + downloader.filename_from_headers)
								elif downloader.filename_from_url and downloader.filename_from_url != "media.mp3":
									logger.info("file name from url "+downloader.filename_from_url)
									if self.check_for_meaning(downloader.filename_from_url):
										downloader.change_filename(rename_from_url = True)

								if downloader.exists:
									downloader.filepath = downloader.new_filepath
									downloader.filename = downloader.new_filename
						
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
						self.episode_title = self.episode_title.rstrip(" ").lstrip("!").replace("–", "-").replace("’", "'").replace("‘","").replace('”', '"').replace('“', '"').replace("—","-")
						if self.spreadsheet_message !="":
							self.episode_title == self.spreadsheet_message + self.episode_title
						if not self.description:
							self.description = ""
						self.description = bs(self.description,"lxml").text
						self.description = self.description.replace(r"\n", " ").replace(r"\'s", 's')
						self.description = self.description.rstrip(" ").lstrip("!").replace("–", "-").replace("’", "'").replace("‘","").replace('”', '"').replace('“', '"').replace("—","-")
						if not self.description:
							self.description == ""
						logger.debug(self.episode_link)
						self.episode_link = self.episode_link.rstrip(" ")	
						if not self.flag_for_epis_table:
							logger.info("this episode is not in db")

							episode_data = {"podcast": self.podcast_id,"episode_title":self.episode_title, "description":self.description, "date_harvested":downloader.datetime, "date":self.episode_date, "harvest_link": self.episode_download_link, "episode_link":self.episode_link, "epis_numb" : self.epis_numb, "epis_seas" : self.epis_seas}
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
						
						if not self.episode_sprsh_check():
							 	connection_count = 0
							 	while not connection_count >= 5:
							 		connection_count +=1
							 		try:
							 			ws.append_row([self.podcast_name, podcasts_dict[self.podcast_name]["serial_mms"], podcasts_dict[self.podcast_name]["rss_filename"], self.episode_title, self.description, self.episode_link, dt.fromtimestamp(int(self.episode_date)).strftime('%B %d %Y'), self.tags_list, self.episode_download_link])
							 			logger.info("a new row appended")
							 			break
							 		except gspread.exceptions.APIError as e:
							 			logger.error(str(e))
							 			sleep(10)
						
						



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
		logger.info("*"*50)
		logger.info(self.podcast_name)
		logger.info("*"*50)
		self.parsing_with_feedparser()

	

def harvest():
	"""
	Checks if podcast name in db. Creates if not. Runs harvester
	"""

	flag_for_podc_table = False
	for podcast_name in podcasts_dict:
		logger.info(podcast_name)
		my_podcast = DbHandler()
		name_dict = my_podcast.db_reader(["podcast_id", "last_issue"],[podcast_name],True)
		if name_dict != []:
			flag_for_podc_table = True
			last_issue = name_dict[0]["last_issue"]
			podcast_id = name_dict[0]["podcast_id"]
		if not flag_for_podc_table:
			my_podcast.table_creator("Podcast",{"podcast_name":podcast_name,"serial_mms":podcasts_dict[podcast_name]["serial_mms"], "serial_pol":podcasts_dict[podcast_name]["serial_pol"],"rss_filename":podcasts_dict[podcast_name]["rss_filename"],"publish_link_ro_record":podcasts_dict[podcast_name]["publish_link_ro_record"],"automated_flag":podcasts_dict[podcast_name]["automated_flag"],"access_policy":podcasts_dict[podcast_name]["access_policy"], "template_name":podcasts_dict[podcast_name]["template_name"]})
			logger.info("Podcast table for {} created. ID - {}".format(podcast_name, my_podcast.my_id))
			podcast_id = my_podcast.my_id
			last_issue = 0

		my_episode = Harvester(podcast_id, podcast_name, podcasts_dict[podcast_name], last_issue)
		my_episode.harvester()

def main():
	harvest()

if __name__ == "__main__":
	main()
