import os
import io
import re
from pymarc import parse_xml_to_array,record_to_xml, Field, Subfield
from bs4 import BeautifulSoup
from datetime import datetime as dt
try:
	from settings import logging, template_folder,start_xml, end_xml, report_folder
except:
	from settings_prod import logging, template_folder,start_xml, end_xml, report_folder
from database_handler import DbHandler
import dateparser
from podcast_dict import serials
import sys
sys.path.insert(0, r"Y:\ndha\pre-deposit_prod\LD_working\alma_tools")
from alma_tools import AlmaTools
logger = logging.getLogger(__name__)
# logger.setLevel('DEBUG')


class RecordCreator():

	""" This class creates or updates records in Alma Production or Sandbox depending on key based on database information


	Attributes
	----------

	episode_title : str
		title of episode
	alma_key : str
		"prod" for production or "sb" for sandbox
	record : pymarc object
		bibliographic record in pymarc 
	template_path : str
		path to xml template for particular podcast_name
	epis_numb :  str
		number of episode (None for most cases)
	epis_seas : str
		season of episode (None for most casts)
		f600_first : str
			content of field 600 1
		f600_second : str
			content of field 600 2
		f600_third : str
			content of field 600 3
		f610_first : str
			content of field 610 1
		f610_second : str
			content of field 610 2
		f610_third : str
			content of field 610 3
		f650_first : str
			content of field 650 1
		f650_second : str
			content of field 650 2
		f650_third : str
			content of field 650 3
		f650_forth : str
			content of field 650 4
		f700_first : str
			content of field 700 1
		f700_second : str
			content of field 700 2
		f700_third  : str
			contend of field 700  3


	Methods
	-------
def __init__(self, key):

	find_episode(self)	
	parsing_added_fields(self, value)
	construct_field(self, my_field)		
	parsing_bib_xml(self)
	record_creating_routine(self, update = False, list_of_podcasts = []):
	"""
	
	def __init__(self, key):


		self.alma_key = key
		self.episode_title = None
		record = None
		self.mms_id = None
		self.template_path = None
		self.epis_numb = None
		self.epis_seas = None
		self.record = None
		self.f600_first = None
		self.f600_second = None
		self.f600_third = None
		self.f610_first = None
		self.f610_second = None
		self.f610_third = None
		self.f650_first = None
		self.f650_second = None
		self.f650_third = None
		self.f650_forth = None
		self.f700_first = None
		self.f700_second = None
		self.f700_third = None


	def find_episode(self):

		"""
		Finds episode in episode_title. Used for Crave and Can be removed as Crave will be removed from list of podcasts

		Returns:
			"episode" + number(str) - new episode_title
		"""

		flag = False
		for el in self.episode_title.split(" "):
			if flag:
				number = str(el)
				flag= False
			if el == "episode":
				flag = True
		return "episode " + number


	
	def parsing_added_fields(self, value):
		

		"""
		Parsing fields added from the spreadsheet to prepare for marc record.
		Parameters:
			value(str) - of particular field as it was in spreadsheet
		Returns:
			indicator1(str) - first indicator
			indicator2(str) - second indicator
			my_list(list)  - of unparsed subfields with their codes

		"""
		logger.debug(value)
		my_list = []
		text = value.split("$")[1:]
		indicators = value.split("$")[0]
		indicator1 = indicators[0]

		if indicator1 == "_":
			indicator1 = ""
		indicator2 = indicators[1]

		if indicator2 == "_":
			indicator2 = ""
		for el in text:
			my_list += [el]

		return( indicator1, indicator2, my_list)

	def construct_field(self, my_field):

		"""
		Makes and adds fields from spreadsheet to record

		Parameters:
			my_field (str) - field how it was taken from google spreadsheet

		"""
		logger.debug(my_field)
		f_number = my_field[0]
		subfields = []

		if my_field[1].rstrip(" ") != "":

			indicator1, indicator2, my_list = self.parsing_added_fields(my_field[1])
			for el in my_list:
			 	subfields += [Subfield(code = el.split(" ")[0], value= " ".join(el.split(" ")[1:]).lstrip(" ").rstrip(" ").rstrip("\t"))]
			field = Field(tag = f_number, indicators = [indicator1, indicator2], subfields = subfields)
			self.record.add_ordered_field(field)

	def parsing_bib_xml_serials(self, my_record_xml):
		"""
		Modifies 500  field.

		"""
		print(my_record_xml)
		try:
			self.record = parse_xml_to_array(my_record_xml)[0]
		except Exception as e:
			logger.error(self.template_path)
			logger.error(str(e))
			quit()
		if self.podcast_name in ["Can I steal you for a second"]:
			field505_a = self.record["505"]["a"]
			my_episodes = field505_a.split(" -- ")
			my_episodes_dict = {}
			for ep in my_episodes:
				number = ep.split(".")[0]
				name = ep.split(". ")[1]
				my_episodes_dict[number] = name
			#my_episodes_dict[self.episode_title.split(".")[0]] = my_episodes_dict[self.episode_title.split(".")[1]]
			temp=sorted(my_episodes_dict)
			my_episodes_dict = dict([(k,my_episodes_dict[k]) for i,k in enumerate(temp)])
			new505 = ""
			for el in my_episodes_dict:
				new505+=el
				new505+=". "
				new505+=my_episodes_dict[el]
				new505+=" -- "
			new505.rstrip(" -- ")
			self.record["505"]["a"] = new505
		bib_data = record_to_xml(self.record)
		bib_data = str(bib_data).replace("\\n", "\n").replace("\\", "")
		self.bib_data = start_xml + bib_data +end_xml

	def parsing_bib_xml(self):
		"""
		Parses template , modifies it and adds new fields. It is also parses episode title according to rules for 245, 490  and 800 or 830 fields.

		"""
		self.record = None

		#this  set is for correct indexing of 245 field

		NON_FILING_WORDS = ( 'the', 'an', 'a', '"the', '"an', '"a' )

		f245 = False 
		f490v= False
		f830v = False

		try:
			self.record = parse_xml_to_array(self.template_path )[0]
		except Exception as e:
			logger.error(self.template_path)
			logger.error(str(e))
			quit()
		number_dictionary = {"one":'1',"two":'2',"three":'3',"four":'4',"five":'5',"six":'6',"seven":'7',"eight":'8',"nine":'9',"zero":'0'}

		##################################################Parsing rules##################################################################
		#This part is very flexible. It is parsing titles to create correct 490 and 800 or 830 field#####################################
		if self.podcast_name in ["Crave!"]:
			# print(self.episode_title)
			# print(self.harvest_link)
			if ":" in self.episode_title and (self.episode_title.split(":")[0][-1].isdigit() or self.episode_title.split(":")[0][-2].isdigit()):
				f245 = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
				f490v = self.episode_title.split(":")[0].replace('Crave ',"").replace("Crave!","").lstrip(" ")
			elif "-" in self.episode_title and (self.episode_title.split("-")[0].rstrip(" ")[-1].isdigit() or self.episode_title.split("-")[0][-2].isdigit()):
				f245= "-".join(self.episode_title.split("-")[1:]).lstrip(" ")
				f490v = self.episode_title.split("-")[0].lstrip(" ").replace('Crave!',"").replace("Crave","").lstrip(" ")
			else:
				logger.info("Crave!!!Check  245 and 490!!!")
				try:
					episode = self.find_episode()
					f245 = self.episode_title.replace("Crave!", "").replace(episode, "").lstrip(" ").lstrip(":").lstrip("-").lstrip(' ')
					f490v = episode
				except:
					f245 = self.episode_title.replace("Crave!", "").lstrip(" ").lstrip(":").lstrip("-").lstrip(' ')
					f490v = None
			if self.episode_title in ["Crave! episode one hundred"]:
				f245 = "Episode one hundred"
				f490v = None

		
		if self.podcast_name in ["CIRCUIT cast"]:
			if ":" in self.episode_title:
				f245 = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
				f490v = self.episode_title.split(":")[0]
			elif "-" in self.episode_title:
				f245= "-".join(self.episode_title.split("-")[1:]).lstrip(" ").rstrip(" ")
				f490v = self.episode_title.split("-")[0].lstrip(" ")

		if self.podcast_name in ["Dirt Church Radio"]:
			if "-" in self.episode_title:
				f245 = self.episode_title.lstrip("DCR").lstrip(" ").split("-")[-1].lstrip(" ")
				f490v = self.episode_title.split("-")[0].rstrip(" ")

		if self.podcast_name in ["Advanced analytics"]:
			if ":" in self.episode_title:
				f245 = self.episode_title.split(":")[-1].lstrip(" ")
				f490v = self.episode_title.split(":")[0].rstrip(" ")
				f830v = str(f490v)
			else:
				f490v = "S{}:E{}".format(self.epis_seas, self.epis_numb)

		if self.podcast_name  in ["Kiwi birth tales"]:
			if ":" in self.episode_title:
				f245 = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
				f490v = self.episode_title.split(":")[0].rstrip(" ")
			elif "-" in self.episode_title:
				f245 = "-".join(self.episode_title.split("-")[1:]).lstrip(" ")
				f490v = self.episode_title.split("-")[0].rstrip(" ")	

		if self.podcast_name in ["Kiwi country"]:
			f245 = self.episode_title.lstrip("Kiwi Country with Georgia").lstrip("Kiwi country with Georgia").lstrip("Kiwi country").lstrip("Kiwi Country")
			# if ":" in self.episode_title and "-" in self.episode_title:
			# 	f245 = self.episode_title.split("-")[-1]
			# 	f490v = self.episode_title.split(":")[1].split("-")[0]
			# elif "-" in self.episode_title:
			# 	f245 = self.episode_title.split("-")[-1]
			# 	f490v = self.episode_title.split("-")[0]
			# elif ":" in self.episode_title:
			# 	f245 = self.episode_title.split(":")[-1]
			# 	f490v = "Episode " +self.episode_title.split(":")[0]
		if self.podcast_name in ["Taringa","The creative spear"]:
			f245 = " - ".join(self.episode_title.split(" - ")[2:]).rstrip(" ").lstrip(" ")
			f490v = self.episode_title.split(" - ")[1].lstrip(' ').rstrip(" ").replace(" |",",")
			f830v = f490v.lower().replace(", ", " ")
		if self.podcast_name in ["Dancing in your head"]:
			pass #placeholder

		if self.podcast_name in ["You're gonna' die in bed"]:
			if not self.episode_title.startswith("Episode"):
				f245 = " - ".join(self.episode_title.split(" - ")[2:]).rstrip(" ").lstrip(" ")
				f490v = self.episode_title.split(" - ")[1].lstrip(' ').rstrip(" ").replace(" |",",")
				f830v = f490v.lower().replace(", ", " ")
			else:
				if "|" in self.episode_title and "-" in episode_title:
					eps = self.episode_title.split("|")[0]
					ssn = self.episode_title.split("|")[-1].split("-")[0]
					f245 = "-".join(self.episode_title.split("-")[1:])
					f490 = "Season " + number_dictionary[ssn.split(" ")[-1]] +", " +"Episode " + number_dictionary[eps.split(" ")[-1]]



		if self.podcast_name in ["A Neesh audience","The lip","Stupid Questions for Scientists","Back to the disc-player podcast","DOC sounds of science podcast",  "All Blacks", "Never Repeats podcast", "The Rubbish trip", "Back to the disc-player podcast", "Snacks and chats","Classic NBL podcast"]:
			if ":" in self.episode_title: 
				f245 = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
				f490v = self.episode_title.split(":")[0].rstrip(" ")
			if f490v:
				try:
					if not "episode" in f490v.lower() and not "ep" in f490v.lower() and not f490v.lower().startswith("e") and not "podcast" in f490v.lower():# and not f490v.lower().startswith("E"):
						f490v = "Episode " + f490v
				except:
					f490v=None


		if self.podcast_name in ["76 small rooms","Dietary requirements", "History of Aotearoa New Zealand podcast", "Musician's Map", "The Frickin Dangerous Bro Show", "Dirt Church Radio","Baboon yodel"]:
			if "-" in self.episode_title:
				f245 = "-".join(self.episode_title.split("-")[1:]).lstrip(" ")
				f490v = self.episode_title.split("-")[0].rstrip(" ")
			if not f490v and self.epis_numb:
				f490v = "Episode " + self.epis_numb
			if self.podcast_name in ["Baboon yodel"]:
				try:
					f490v = "Episode " + self.epis_numb
				except:
					f490v = None

		if self.podcast_name in ["On the rag" , "Papercuts" , "The real pod" , "The Offspin podcast", "Taxpayer talk","The fold"]:
			if ":" in self.episode_title:
				f245 = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")

		if self.podcast_name in ["Phoenix city"]:
			if "-" in self.episode_title:
				f245 = "-".join(self.episode_title.split("-")[1:]).lstrip(" ").rstrip(" ")

		if self.podcast_name in ["Love this podcast"]:
			if not self.episode_title.split(" ")[-1].startswith("(E"):
				if "-" in self.episode_title:
					f245 = "-".join(self.episode_title.split("-")[1:]).lstrip(" ").rstrip(" ")
					f490v = self.episode_title.split("-")[0]
				if "–" in self.episode_title:
					f245 = "–".join(self.episode_title.split("-")[1:]).lstrip(" ").rstrip(" ")
					f490v = self.episode_title.split("–")[0]
			else:
				if "(" in self.episode_title:
					f245 = " ".join(self.episode_title.split(" ")[:-1])
					f490v = self.episode_title.split(" ")[-1].strip("()")
			f830v = str(f490v)
		
		if self.podcast_name == "Ciaran McMeeken":
			if "//" in self.episode_title:
				f245 = ":".join(self.episode_title.split("//")[1:]).lstrip(" ")
				f490v = self.episode_title.split("//")[0].rstrip(" ")
							
		if self.podcast_name in ["Better off read"]:
			if "Ep " in self.episode_title or "Episode" in self.episode_title:
					f245 = " ".join(self.episode_title.split(" ")[2:])
					f490v = " ".join(self.episode_title.split(" ")[:2]).rstrip(":")
					f830v = f490v.lower()

		if self.podcast_name in ["The Angus Dunn"]:
			if "The Angus Dunn Podcast " in my_alma.xml_response_data:
				f245 = my_rec["245"]["a"].lstrip("The Angus Dunn Podcast ")
				if "-" in f245:
					divider = "-"
				if ":" in f245:
					divider = ":"
				f490v =f245.split(divider)[0]
				f830v = f490v.lower()+"."
				f245a = divider.join(f245.split(divider)[1:])
				
		if self.podcast_name in ["Business is boring"]:
			if "Business is boring" in self.episode_title:
				f245 = self.episode_title.lstrip("Business is boring").lstrip(" ").lstrip(":").lstrip(" ")
			if "Business is Boring" in self.episode_title:
				f245 = self.episode_title.lstrip("Business is Boring").lstrip(" ").lstrip(":").lstrip(" ")


		if self.podcast_name in ["HP business class"]:
			#self.episode_title = self.episode_title.lstrip('HP business class').lstrip("Business Class").lstrip(' ').lstrip(':').lstrip(' ')
			if ":" in self.episode_title:
				f245 = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
				f490v = self.episode_title.split(":")[0].rstrip(' ')
			else:
				f245 =str(self.episode_title)
		if self.podcast_name in ['New Zealand Brewer']:
			if "-" in self.episode_title:
				if not self.episode_title.startswith("NZB"):
					f245 = self.episode_title.split("-")[0].rstrip(" ")
					if self.episode_title.split("-")[0].lstrip(" ").startswith("NZB"):
							f490v = "Episode " + self.episode_title.split("Episode ")[-1].lstrip(" ")
				else:
					f245 = self.episode_title.split("-")[-1].rstrip(" ").lstrip(" ")
					f490v = "Episode " + self.episode_title.split("-")[0].lstrip(" ").split("Episode")[-1].lstrip(" ")



		# if self.podcast_name in ["Bhuja podcast"]:
		# 	#self.episode_title = self.episode_title.lstrip('HP business class').lstrip(' ').lstrip(':').lstrip(' ')
		# 	if ":" in self.episode_title:
		# 		f245 = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
		# 		f490v = self.episode_title.split(":")[0].rstrip(' ')
		# 	elif '.' in self.episode_title:
		# 		f245 = ".".join(self.episode_title.split(".")[1:]).lstrip(" ")
		# 		f490v = self.episode_title.split(".")[0].rstrip(' ')
		# 	elif '-' in self.episode_title:
		# 		f245 = "-".join(self.episode_title.split("-")[1:]).lstrip(" ")
		# 		f490v = self.episode_title.split("-")[0].rstrip(' ')
		# 	else:
		# 		f245 =str(self.episode_title)

		if self.podcast_name in ["Mud & blood"]:
			if ":" in self.episode_title:
				if self.episode_title.split(":")[0].isdigit():
					f245 = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
					f490v = self.episode_title.split(":")[0].rstrip(' ')

		if self.podcast_name in ["Few good men","Stag roar"]:
			if ":" in self.episode_title:
				f245 = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
				f490v = self.episode_title.split(":")[0].rstrip(' ')
			elif '-' in self.episode_title:
				f245 = "-".join(self.episode_title.split("-")[1:]).lstrip(" ")
				f490v = self.episode_title.split("-")[0].rstrip(' ')

		if self.podcast_name in ["Bosses rebuilding"]:
			if "Bosses Rebuilding:" in self.episode_title:
				f245 = self.episode_title.split("Rebuilding:")[-1]

		if "Bosses in Lockdown" in self.episode_title:
				f245 = self.episode_title.split("in Lockdown:")[-1]

		if self.podcast_name in ["Dr. Tennant's verbal highs"]:
			if ":" in self.episode_title:
				f245 = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
				f490v = self.episode_title.split(":")[0].rstrip(' ')

		if self.podcast_name in ["Girls on top"]:
			if "-" in  self.episode_title and self.episode_title.startswith("Episode"):
				f245 = "-".join(self.episode_title.split("-")[1:]).lstrip(" ")
				f490v = self.episode_title.split("-")[0].rstrip(' ')
		
		if self.podcast_name in ["Untamed Aotearoa"]:
			if "#" in  self.episode_title:
				f245 = "#".join(self.episode_title.split("#")[1:]).lstrip(" ")
				f490v = "# "+ self.episode_title.split("#")[0].rstrip(' ')
			
		if self.podcast_name in ["NZ tech podcast with Paul Spain"]:
			# print(self.episode_title)
			if  ":" in self.episode_title and ("NZ Tech Podcast" in self.episode_title or "Episode" in self.episode_title) and not "Running time" in self.episode_title:
				ep_number = None
				# print(self.episode_title)
				if ": NZ Tech Podcast" in self.episode_title:
					f245 =  ":".join(self.episode_title.split(":")[:-1])
					ep_number = re.findall(r'[0-9]+', self.episode_title.split(":")[-1])[0]
				elif "NZ Tech Podcast" in self.episode_title:
					f245 = ":".join(self.episode_title.split(":")[1:])
					try:
						ep_number = re.findall(r'[0-9]+', self.episode_title.split(":")[0])[0]
					except:
						logger.info("no episode number")
				elif ": Episode"	 in self.episode_title:
					ep_number = re.findall(r'[0-9]+', self.episode_title.split(":")[1])[0]
				elif self.episode_title.startswith("Episode"):
					ep_number = re.findall(r'[0-9]+', self.episode_title.split(":")[0])[0]

			elif "- NZ Tech Podcast" in self.episode_title:
					f245 =  "-".join(self.episode_title.split(":")[:-1])
			if f245 and ep_number:
				try:
					f490v = str(ep_number)
					f830v = "episode "+ep_number
				except:
					pass
			
		if self.podcast_name in ["Retrogasmic"]:
			if " Se" in self.episode_title and  " Ep" in self.episode_title:
				f245 = "Se".join(self.episode_title.split("Se")[:-1]).rstrip(" ")
				f490v = "Se"+self.episode_title.split("Se")[-1].lstrip(" ").replace("..", ".")
		
			elif " Ep" in self.episode_title:
				f245 = "Ep".join(self.episode_title.split("Ep")[:-1]).rstrip(" ")
				f490v = "Ep "+self.episode_title.split("Ep")[-1].lstrip(" ").replace("..", ".")
				f830v = "ep. "+self.episode_title.split("Ep")[-1].lstrip(" ").replace("..", ".")
		if self.podcast_name in ["EPIC podcast"]:
			f245 = self.episode_title.lstrip("The EPIC Podcast - ").lstrip("The Epic Podcast - ").lstrip("The EPIC Podcast ").lstrip("The Epic Podcast ")
			f490v = f245.split("-")[0].strip(" ")
			f245 = f245.split("-")[-1].strip(" ")
			if " " in f490v and not "ep" in f490v.lower():
					f490v = f490v.replace(" ",":")
			f830v = f490v+ "."

		if self.podcast_name in ["Indegious_Urbanism", "Alchemy","Stirring the pot", "Selfie reflective", "UC science radio"]:
			f245 = str(self.episode_title)
			if self.epis_numb:
				f245 = self.episode_title.strip(self.epis_numb).rstrip(" ").lstrip(" ")
				if self.epis_seas:
					f490v = "S{}:E{}".format(self.epis_seas, self.epis_numb)
				else:
					if self.podcast_name in ["Alchemy"]:
						f490v = str(self.epis_numb)
					else:
						f490v ="Episode " +  self.epis_numb
		if self.podcast_name in ["Queenstown life", "Animal matters", "Windows on dementia"]:
			f490v ="Episode " +  self.epis_numb

		if self.podcast_name in ["Property Academy"]:
			if "⎮" in self.episode_title:
				divider = "⎮"
			else:
				divider = "|"
			f245 = "|".join(self.episode_title.split(divider)[:-1])
			f490v = self.episode_title.split(divider)[-1]

		if self.podcast_name == "Chris and Sam podcast":
			f245 = self.episode_title.split(" | ")[0]
			if  " | EP" in self.episode_title:
				f490v = "EP"+self.episode_title.split("EP")[1].split(" ")[0]
			elif "EP" in self.episode_title:
				f245 = self.episode_title.split("EP")[0]
				if " - " in self.episode_title:
					f490v="EP" + self.episode_title.split("EP")[1].split(" - ")[0]
		if self.podcast_name in  ["Dont give up your day job"]:
			f245  = " ".join(self.episode_title.split(" ")[2:])
			f490v = " ".join(self.episode_title.split(" ")[:2])
		if self.podcast_name in ["thehappy$aver.com.", "Family whanau and disability"]:
			if "." and self.episode_title and self.episode_title.split(".")[0].isdigit():
				f245 =".".join(self.episode_title.split(".")[1:]).lstrip(" ")
				f490 ="Episode "+self.episode_title.split('.')[0]
		if f490v and not f830v:
			f830v = f490v.lower() 

		##########################################################################################################################################################################################################################################

		# Field 008

		new008 = ""
		lst008 = list(self.record["008"].data)

		for ind in range(len(lst008)):

			if ind == 7:
				lst008[ind] = self.year[0]
			if ind == 8:
				lst008[ind] = self.year[1]
			if ind == 9:
				lst008[ind] =self.year[2]
			if ind == 10:
				lst008[ind] = self.year[3]
			new008 +=lst008[ind]
		
		field = Field(tag = '008', data =new008)
		self.record.remove_fields("008")
		self.record.add_ordered_field(field)  

		#f100

		additional_fields_list = [["100", self.f100]]

		for fld in additional_fields_list:
			if fld[1]:
				self.construct_field(fld)
		
		
		#Field 245
		dot_or_something = "."

		
		if self.episode_title.rstrip(" ").endswith("?") or self.episode_title.rstrip(" ").endswith("!") or self.episode_title.rstrip(" ").endswith("."):
			dot_or_something = ""

		self.record["245"]["a"] = self.episode_title + dot_or_something
		if f245:
			if f245.rstrip(" ").endswith("?") or f245.rstrip(" ").endswith("!") or f245.rstrip(" ").endswith("."):
				dot_or_something = ""
			self.record["245"]["a"] = f245 + dot_or_something
		if "100" in self.record or "110" in self.record:
			self.record["245"].indicators =["1","0"]
		else:
			self.record["245"].indicators = ["0","0"]
		title_words =self.record["245"]["a"].split(' ')

		if title_words[0].lower() in NON_FILING_WORDS:

			if title_words[0] in ["The",'“An','"An']:
				self.record["245"].indicators[1] = '4' 
			elif title_words[0] == "A" or title_words[0]:
				self.record["245"].indicators[1] = '2'
			elif title_words[0] in ["An",'“A','"A']:
				self.record["245"].indicators[1] = '3'
			elif title_words[0] in ['“The','"The']:
				self.record["245"].indicators[1] = '5'
		
		#Field 264

		self.record["264"]["c"] = "[{}]".format(self.year)


		#Field 490

		try:
			my_date = dt.fromtimestamp(int(self.date)).strftime('%B %d, %Y')
		except ValueError:
			my_date = dateparser.parse(self.date).strftime('%B %d, %Y')
		if f490v:
			self.record["490"]["v"] = f490v
		else:
			try:
				self.record["490"]["v"] = dt.fromtimestamp(int(self.date)).strftime('%B %d, %Y')
			except ValueError:
				self.record["490"]["v"]= my_date

		#Field 520
		self.description = self.description#.replace#("&nbsp;"," ")
		try:
			self.record["520"]["a"] = '"{}"--RSS feed.'.format(self.description)
		except:
			logger.debug("No description")

		#Fields 600, 610, 650,  700, 710

		additional_fields_list = [["600", self.f600_first], ["600",self.f600_second], ["600",self.f600_third], ["610",self.f610_first], ["610",self.f610_second], ["610",self.f610_third], ["650",self.f650_first], ["650",self.f650_second], ["650",self.f650_third], ["650",self.f650_forth], ["700",self.f700_first], ["700",self.f700_second], ["700",self.f700_third]]
		for fld in additional_fields_list:
			if fld[1]:
				self.construct_field(fld)

		#reo 650 changing orders
		my_field = None
		for ind in range(len(self.record.get_fields('650'))-1):

			if self.record.get_fields('650')[ind]["a"] == "Kōnae ipurangi.":
			#	print("HERE")
				my_subfield = self.record.get_fields("650")[ind]["a"]
			#	print(my_subfield.encode("utf-8"))
				my_field = self.record.get_fields("650")[ind]
				self.record.remove_field(my_field)


		if my_field:	#print(self.record.get_fields("650")[ind].value().encode("utf-8"))
			self.record.add_ordered_field(my_field)

		#Field 830 or 800

		if "830" in self.record:
			if f830v:
				self.record["830"]["v"] = f830v + "."
			else:
				self.record["830"]["v"] = my_date + "."
		elif "800" in self.record:
			if f830v:
				self.record["800"]["v"] = f830v + "."
			else:
				self.record["800"]["v"] = my_date + "."

		elif "830" in self.record:
			if f830v:
				self.record["810"]["v"] = f830v + "."
			else:
				self.record["810"]["v"] = my_date + "."
		#Field 856
		
		my_fields = self.record.get_fields("856")
		for ind in  range(len(self.record.get_fields("856"))):
			ndha_archived_flag=False
			subfields = self.record.get_fields("856")[ind].subfields
			indicators = self.record.get_fields('856')[ind].indicators
			#For updates to exlude automated field
			for sld in subfields:
				if sld.code == "z":
					idha_archived_flag = True
			if not ndha_archived_flag:
				#datafield tag="856" ind1="4" ind2="0"><subfield code="u"></subfield></datafield><datafield tag="856" ind1="4" ind2="2"><subfield code="3">File host</subfield><subfield code="u">&lt;insert page URL&gt;</subfield></datafield><datafield tag="901" ind1="" ind2=""><subfield code="a">MGR</subfield></datafield></recor
				print(subfields)
				print(len(subfields))
				if len(subfields) == 1:
					for idx in range(len(subfields)):
						if subfields[idx].code =="u":
							subfields[idx] = Subfield(code='u', value=self.harvest_link)
					field1 = Field(tag = "856", indicators = indicators, subfields = subfields)
				elif len(subfields) == 2:
					for idx in range(len(subfields)):
						if subfields[idx].code  == "u":
							subfields[idx] = Subfield(code='u', value=self.episode_link)

					field2 = Field(tag = "856", indicators = indicators, subfields = subfields)

		logger.debug(str(self.record))
		self.record.remove_fields("856")
		self.record.add_ordered_field(field1)
		if self.episode_link:
			self.record.add_ordered_field(field2)
			print(self.record)

		bib_data = record_to_xml(self.record)
		bib_data = str(bib_data).replace("\\n", "\n").replace("\\", "")
		self.bib_data = start_xml + bib_data +end_xml	
		
	def record_creating_routine(self, update = False, list_of_podcasts = []):

		"""
		Manages process of creating if update set False or updating record for all the podcasts in db which have tick or tick and mms_id for updating.
		Parameters:
			update(bool) - set False by default to create record or True to update
			list_of_podcasts(list) - to or update records for particular podcast
		"""

		if update:
			logger.info("Updating alma record")
		else:
			logger.info("Creating Alma record")
		my_db = DbHandler()
		my_dict=my_db.db_reader(
			["podcast_name", "podcast_id", "serial_mms","rss_link","location","publish_link_to_record","episode_title","mis_mms","ie_num","tags","description",
			"date","episode_link","harvest_link","date_harvested","f100","f600_first","f600_second","f600_third","f610_first",
			"f610_second","f610_third","f650_first","f650_second","f650_third","f650_forth","f655","f700_first","f700_second",
			"f700_third","f710_first","f710_second","f710_third", "template_name","tick", "epis_numb", "epis_seas"],list_of_podcasts
			)
		for epis  in my_dict:
			self.podcast_name = epis["podcast_name"]
			self.podcast_id = epis["podcast_id"]
			self.serial_mms = epis["serial_mms"]
			self.rss_link = epis["rss_link"]
			self.location = epis["location"]
			self.publish_link_to_record = epis["publish_link_to_record"]

			if "tick" in epis.keys() and epis["tick"] and not epis["serial_mms"] in serials:
					self.mms_id = epis["mis_mms"]
					logger.debug(epis["podcast_name"])
					logger.debug(epis["episode_title"])
					self.template_path = os.path.join(template_folder, epis["template_name"])
					try:
						self.year = str(dt.fromtimestamp(int(epis["date"])).strftime('%d %m %Y')).split(" ")[-1]
					except ValueError:
						self.year = dateparser.parse(epis["date"]).strftime("%Y")
						print(self.year)
						print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
					self.episode_title = epis["episode_title"]
					self.tags = epis["tags"]
					self.description = epis["description"]
					self.date = epis["date"]
					self.episode_link = epis["episode_link"]
					self.harvest_link = epis["harvest_link"]
					self.date_harvested = epis["date_harvested"]
					self.f100 = epis["f100"]
					self.f600_first = epis["f600_first"]
					self.f600_second = epis["f600_second"]
					self.f600_third = epis["f600_third"]
					self.f610_first = epis["f610_first"]
					self.f610_second = epis["f610_second"]
					self.f610_third = epis["f610_third"]
					self.f650_first = epis["f650_first"]
					self.f650_second = epis["f650_second"]
					self.f650_third = epis["f650_third"]
					self.f650_forth = epis["f650_forth"]
					self.f655_first = epis["f655"]
					self.f700_first = epis["f700_first"]
					self.f700_second = epis["f700_second"]
					self.f700_third = epis["f700_third"]
					self.f710_first = epis["f710_first"]
					self.f710_second = epis["f710_second"]
					self.f710_third = epis["f710_third"]
					self.epis_numb = epis["epis_numb"]
					self.epis_seas = epis["epis_seas"]
					self.parsing_bib_xml()
					logger.debug(self.bib_data)
					my_alma = AlmaTools(self.alma_key)
					if not update:
						if not self.mms_id:		
							my_alma.create_bib(self.bib_data)
							logger.debug(my_alma.xml_response_data)
							logger.debug(my_alma.status_code)
							if my_alma.status_code == 200:
								bib_grab = BeautifulSoup( my_alma.xml_response_data, 'lxml-xml' )
								try:
									self.mms_id = bib_grab.find( 'bib' ).find( 'mms_id' ).string
									statement = 'MMS_ID: '+self.mms_id + " " +str(my_alma.xml_response_data)
									logger.debug(statement)
									logger.info(self.mms_id+ " - record created for "+self.episode_title)
									with open (os.path.join(report_folder, "mms.txt"),"a" ) as mms_file:
										mms_file.write( self.mms_id )
										mms_file.write("\n")
									with io.open(os.path.join(report_folder,"mms_titles.txt"),"a", encoding="utf-8") as mms_title_file:
										mms_title_file.write("{}|{}".format(self.mms_id, self.episode_title))
										mms_title_file.write("\n")
								except Exception as e:
									print(str(e))
									quit()
									statement =  "Could not grab mms from {}. {}".format ( my_alma.xml_response_data, str(e)  ) 
									logger.error(statement)
						if self.mms_id:
							my_db.db_update_mms (self.mms_id, self.episode_title, self.podcast_id)
								
					else:
						if self.mms_id:
							logger.info("Updating record "+ self.mms_id)
							my_alma.update_bib(self.mms_id, self.bib_data)
							logger.debug(my_alma.status_code)
							logger.debug(my_alma.xml_response_data)
							if my_alma.status_code ==200:
								logger.info("updated")
							else:
								logger.error(my_alma.xml_response_data)
								quit()


			elif "tick" in epis.keys() and epis["tick"] and epis["serial_mms"] in serials:
				print(epis)
				my_alma = AlmaTools(self.alma_key)
				my_alma.get_bib(self.serial_mms)
				self.episode_title = epis["episode_title"]
				my_record_xml = parse_xml_to_array(io.StringIO(my_alma.xml_response_data))[0]
				self.parsing_bib_xml_serials(my_record_xml)
				my_alma.update_bib(self.serial_mms, self.bib_data)
				if my_alma.status_code ==200:
					logger.info("updated")
					my_db.db_update_updated(self.mms_id)
				else:
					logger.error(my_alma.xml_response_data)
					quit()

				
					
	

def main():

	"""This function is example. Runs record creating process for particular podcasts. Set True for updating. Not creating.
	Change to sb if test required
	"""

	my_rec = RecordCreator("prod")
	my_rec.record_creating_routine(True, ["The real pod"])#,"Taxpayer talk", "The fold", "Love this podcast"])
	#my_rec.record_creating_routine(True, [])


if __name__ == '__main__':

	main()