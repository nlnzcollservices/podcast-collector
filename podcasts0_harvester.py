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
from settings import  file_folder, report_folder, podcast_sprsh, logging,creds #!!!! report

#######################################Creating google spreadsheet object#################################################


c = gspread.authorize(creds)
gs = c.open_by_key(podcast_sprsh)
#change if the name or id of the worksheet is different
ws = gs.get_worksheet(0)

	
class Harvester():

	def __init__(self, podcast_id, podcast_name, podcast_data, last_issue):
		
		"""
		   Harvests podcast episodes via rss feed.

		   podcast_name(str) - name of podcast from podcasts_dict. Should be the same as in serial_record
		   podcast_data(dict) - dictionary which contains information about particular podcast
		"""
		self.podcast_id = podcast_id
		self.podcast_name = podcast_name
		self.podcast_data = podcast_data
		self.last_issue = last_issue

	def reload_spreadsheet(self, function, parameters):
	
		c = gspread.authorize(creds)
		gs = c.open_by_key(podcast_sprsh)
		ws = gs.get_worksheet(0)
		function(ws, parameters)

	def episode_sprsh_check(self):
		
		logging.info("Checking {} in the spreadsheet".format(self.episode_title))
		rng = "D2:D{}".format(ws.row_count)	
		try:
			cell_range = ws.range(rng)
			logging.info("cell range found")
		except gspread.exceptions.APIError as e:
			logging.debug(str(e))
			sleep(10)
			self.reload_spreadsheet(self.episode_sprsh_check, None)
			cell_range = ws.range(rng)
		for row in cell_range:
			if row.value == self.episode_title:
				if ws.acell(f"F{row.row}").value == "!!!":
				# the title exists but is not harvested well	
					return False 
				#the title exists
				return True #

		

	def jhove_check(self, filepath):

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
			logging.info("could not find with podcastparser")
			logging.info(str(e))
			logging.info(type(e))
			self.description = None
	


	def parsing_with_feedparser(self):

		self.pisode_download_link = None
		self.episode_download_link = None
		print("here")

		d = feedparser.parse(self.podcast_data["rss_filename"])
		print(d)
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
			try:
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
							self.episode_date = mktime(dt.strptime(self.episode_date,"%a, %d %b %Y %H:%M:%S +0000").timetuple())


				max_time =  float(self.last_issue)
				if float(int(self.episode_date)) > max_time:
					logging.info("A new episode")
					self.time_flag = True		
			except Exception as e:
				logging.warning("CANNOT PARSE DATE" + str(e))
			self.episode_title  = d["entries"][ind]["title"]	
			if self.time_flag:# and self.title_flag:
				logging.info(self.episode_title)
				try:
					self.episode_link = d["entries"][ind]["link"]
				except:
					pass
				logging.info(self.episode_link)			
				if self.episode_title:# in ["Living the designer's life, while the world watches • Charli Prangley, Design & YouTube superstar", "Creating a feast for the eyes, heart and mind • Natasha Lampard, Co-founder, Webstock","Storytelling with holographic maps • Chris Hay, founder of Locales","Master class in launching a startup • Sonya Williams, co-founder of Sharesies"]:
					print(d["entries"][ind]["links"])
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
						logging.info(f"episode download link {self.episode_download_link}")
					except Exception as e:
						logging.debug(str(e))
					if self.podcast_name in ["Taxpayer talk"] and not self.episode_link:
						self.episode_link = self.episode_download_link.split(".mp3")[0]
					if self.podcast_name in ["Top writers radio show", "Dont give up your day job"]:
						self.episode_link = ""
					try:	
							tags_list = ""
							tags = d["entries"][ind]["tags"]
							for  idx in range(len(tags)):
								tags_list+= tags[idx]["term"]
								tags_list += ", "
							self.tags_list = tags_list.rstrip(', ')

					except Exception as e:
						logging.info(str(e))
						logging.info("could not find tags")

					if not self.description:
						try:
							self.description =  d["entries"][ind]["summary_detail"]["value"]

							if "[&#8230;]" in self.description:							
								self.description = d["entries"][ind]["content"][0]["value"]
						except KeyError:
							logging.debug("could not get description by summary details")
							quit()
						except Exception as e:
							print(str(e))

					if not self.description:
						try:
							logging.debug("podcastparser description")
							self.find_description_with_podcastparser()
							self.description = self.description2
						except Exception as e:
							logging.degub(str(e))

					if not self.description:
						logging.debug("!!!No description!!!")
						

					if self.podcast_name in ["Human-robot interaction podcast"]:
						self.find_description_with_podcastparser()
						if self.description2:
							self.description = self.description+" "+ self.description2
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
						downloader = Downloader(self.episode_download_link, self.f_path, collect_html=False, proxies=None)
						logging.info(downloader.message)
						
						if downloader.size_original == 0:
							logging.info("Ther is empty file on {} in {} of {}. Please contact publisher".format(episode_download_link, episode_title, podcast_name))
							self.spreadsheet_message = "!!!D Not Tick. Empty file. Ask piblisher!!!"
						if not downloader.download_status or not self.jhove_check(downloader.filepath) or (downloader.filesize == 0 and downloader.size_original != 0):
							downloader = Downloader(self.episode_download_link, self.f_path, collect_html=False, proxies=None)
							if not downloader.download_status:
								downloader.message
							if not self.jhove_check(downloader.filepath):
								logging.debug("File is not well-formed")
								quit()



						if downloader.filename_from_headers or downloader.filename_from_url:
							if downloader.filename_from_headers or downloader.filename_from_url:
								if downloader.filename_from_headers and downloader.filename_from_headers != "media.mp3":									
									if self.check_for_meaning(downloader.filename_from_headers):
										downloader.change_filename(rename_from_headers = True)
										logging.info(f"filename from headers {downloader.filename_from_headers}")
								elif downloader.filename_from_url and downloader.filename_from_url != "media.mp3":
									logging.info(f"file name from url {downloader.filename_from_url}")
									if self.check_for_meaning(downloader.filename_from_url):
										downloader.change_filename(rename_from_url = True)

								if downloader.exists:
									downloader.filepath = downloader.new_filepath
									downloader.filename = downloader.new_filename
						
						my_podcast = DbHandler()
						episode_dict = my_podcast.db_reader(["episode_title"],[self.podcast_name],True)
						for epsd in episode_dict:
							if not epsd == {}:
								if epsd["episode_title"] == self.episode_title:
									logging.info(f"the episode {self.episode_title} is in db")
									self.flag_for_epis_table = True


						try:
							file_dict = my_podcast.db_reader(["filepath"], [self.podcast_name], True)
							for flpth in file_dict:
								if not flpth =={}:
									if flpth["filepath"] == downloader.filepath:
										self.flag_for_file = True
										logging.info(f"the file {downloader.filepath} exists")
						except KeyError as e:
							logging.debug(str(e))

												## Cleaning part##
						
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
						print(self.episode_link)
						self.episode_link = self.episode_link.rstrip(" ")	
						if not self.flag_for_epis_table:
							logging.info("this episode is not in db")

							episode_data = {"podcast": self.podcast_id,"episode_title":self.episode_title, "description":self.description, "date_harvested":downloader.datetime, "date":self.episode_date, "harvest_link": self.episode_download_link, "episode_link":self.episode_link, "epis_numb" : self.epis_numb, "epis_seas" : self.epis_seas}
							my_podcast.table_creator("Episode", episode_data)
							episode = my_podcast.my_id.id
							
						if not self.flag_for_file:
							if self.flag_for_epis_table:
								id_dict = my_podcast.db_reader(["episode_id","episode_title"],[self.podcast_name],True)
								for el in id_dict:
									if el["episode_title"] == self.episode_title:
										episode =  el["episode_id"]
	
							logging.info("this file is not in db")

							file_data = {"episode" : episode, "filepath" : downloader.filepath, "md5sum" : downloader.md5, "md5_from_file" : downloader.md5_original, "filesize" : downloader.filesize, "size_original" : downloader.size_original, "file_type" : downloader.filetype_extension}
							my_podcast.table_creator("File", file_data)
						
						if not self.episode_sprsh_check():
							 	connection_count = 0
							 	while not connection_count >= 5:
							 		connection_count +=1
							 		try:
							 			ws.append_row([self.podcast_name, podcasts_dict[self.podcast_name]["serial_mms"], podcasts_dict[self.podcast_name]["rss_filename"], self.episode_title, self.description, self.episode_link, dt.fromtimestamp(int(self.episode_date)).strftime('%B %d %Y'), self.tags_list, self.episode_download_link])
							 			logging.info("a new row appended")
							 			break
							 		except gspread.exceptions.APIError as e:
							 			logging.debug(str(e))
							 			sleep(10)
						
						



	def check_for_meaning(self, my_filename):

		"""Checks filename for possible meaningfull words
		Parameters:
			my_filename (str) - filename to check
		Returns:
			word_meaning_flag(bool) - set True if meaningfull word found
		"""
		word_meaning_flag = False
		lst1  = []
		lst2 = []
		logging.info(f"Checking for meaning {my_filename}")
		if "." in my_filename:
			my_filename = my_filename.split(".")[0]
		if "-" in my_filename:
			lst1 = my_filename.split("-")
		if "_" in my_filename:
			lst2=my_filename.split("_")
		lst = lst1+lst2
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
		print("*"*50)
		print(self.podcast_name)
		print("*"*50)
		self.parsing_with_feedparser()
		print("here")
	

def harvest():

	flag_for_podc_table = False
	for podcast_name in podcasts_dict:
		print(podcast_name)
		my_podcast = DbHandler()
		name_dict = my_podcast.db_reader(["podcast_id", "last_issue"],[podcast_name],True)
		print(name_dict)
		if name_dict != []:
			flag_for_podc_table = True
			last_issue = name_dict[0]["last_issue"]
			podcast_id = name_dict[0]["podcast_id"]

		if not flag_for_podc_table:
			my_podcast.table_creator("Podcast",{"podcast_name":podcast_name,"serial_mms":podcasts_dict[podcast_name]["serial_mms"], "serial_pol":podcasts_dict[podcast_name]["serial_pol"],"rss_filename":podcasts_dict[podcast_name]["rss_filename"],"publish_link_ro_record":podcasts_dict[podcast_name]["publish_link_ro_record"],"automated_flag":podcasts_dict[podcast_name]["automated_flag"],"access_policy":podcasts_dict[podcast_name]["access_policy"], "template_name":podcasts_dict[podcast_name]["template_name"]})
			logging.info(f"Podcast table for {podcast_name} created. ID - {my_podcast.my_id}")
			podcast_id = my_podcast.my_id
			last_issue = 0

		my_episode = Harvester(podcast_id, podcast_name, podcasts_dict[podcast_name], last_issue)
		my_episode.harvester()

def main():
	harvest()

if __name__ == "__main__":
	main()
