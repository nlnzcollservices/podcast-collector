import os
import re
from pymarc import parse_xml_to_array,record_to_xml, Field 
from bs4 import BeautifulSoup
from datetime import datetime as dt
from settings import logging, template_folder,start_xml, end_xml, report_folder#, podcast_sprsh, 
from database_handler import DbHandler
from alma_tools import AlmaTools



class RecordCreator():

	"""
	Creating bibliographical records in Alma sandbox or production depending. Can update existing records using Alma mms id.

	"""
	def __init__(self, key):

		""" Creating records in Alma Production or Sandbox depending on key
		Arguments:
		key(str) - could be "prod" for Prodiction or "sb" for Sandbox
		self.key = key
		Methods:

		"""
		self.alma_key = key

	def find_episode(self):

		flag = False
		for el in self.episode_title.split(" "):
			if flag:
				number = el
				flag= False
			if el == "episode":
				flag = True
		return "episode " + number


	
	def parsing_added_fields(self, value):

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


		f_number = my_field[0]
		subfields = []

		if my_field[1].rstrip(" ") != "":

			indicator1, indicator2, my_list = self.parsing_added_fields(my_field[1])
			for el in my_list:
				subfields += [el.split(" ")[0]]
				subfields += [" ".join(el.split(" ")[1:]).lstrip(" ").rstrip(" ")]
			field = Field(tag = f_number, indicators = [indicator1, indicator2], subfields = subfields)
			self.record.add_ordered_field(field)

	def parsing_bib_xml(self):

		#this  set is for correct indexing of 245 field
		NON_FILING_WORDS = ( 'the', 'an', 'a', '"the', '"an', '"a' )
		f245 = False 
		f490v= False
		f830v = False
		# print(self.podcast_name)
		# print(self.template_path)
		self.record = parse_xml_to_array(self.template_path )[0]

		##################################################Parsing rules##################################################################

		if self.podcast_name in ["Crave!"]:
			if ":" in self.episode_title and (self.episode_title.split(":")[0][-1].isdigit() or self.episode_title.split(":")[0][-2].isdigit()):
				f245 = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
				f490v = self.episode_title.split(":")[0].replace('Crave ',"").replace("Crave!","").lstrip(" ")
			elif "-" in self.episode_title and (self.episode_title.split("-")[0].rstrip(" ")[-1].isdigit() or self.episode_title.split("-")[0][-2].isdigit()):
				f245= "-".join(self.episode_title.split("-")[1:]).lstrip(" ")
				f490v = self.episode_title.split("-")[0].lstrip(" ").replace('Crave!',"").replace("Crave","").lstrip(" ")
			else:
				logging.info("Crave!!!Check  245 and 490!!!")
				episode = self.find_episode()
				f245 = self.episode_title.replace("Crave!", "").replace(episode, "").lstrip(" ").lstrip(":").lstrip("-").lstrip(' ')
				f490v = episode
		
		if self.podcast_name in ["CIRCUIT cast"]:
			if ":" in self.episode_title:
				f245 = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
				f490v = self.episode_title.split(":")[0]
			elif "-" in self.episode_title:
				f245= "-".join(self.episode_title.split("-")[1:]).lstrip(" ").rstrip(" ")
				f490v = self.episode_title.split("-")[0].lstrip(" ")

		if self.podcast_name in ["Dirt Church Radio"]:
			if "-" in self.episode_title:
				self.episode_title = self.episode_title.lstrip("DCR").lstrip(" ")
				f245 = self.episode_title.split("-")[-1].lstrip(" ")
				f490v = self.episode_title.split("-")[0].rstrip(" ")

		if self.podcast_name in ["Advanced analytics"]:
			if ":" in self.episode_title:
				f245 = self.episode_title.split(":")[-1].lstrip(" ")
				f490v = self.episode_title.split(":")[0].rstrip(" ")
				f830v = str(f490v)

		if self.podcast_name in ["Taringa","The creative spear"]:
			f245 = " - ".join(self.episode_title.split(" - ")[2:]).rstrip(" ").lstrip(" ")
			f490v = self.episode_title.split(" - ")[1].lstrip(' ').rstrip(" ")

		if self.podcast_name in ["A Neesh audience","The lip","Stupid Questions for Scientists","Back to the disc-player podcast","DOC sounds of science podcast",  "All Blacks", "Never Repeats podcast", "The Rubbish trip", "Back to the disc-player podcast", "Snacks and chats"]:
			if ":" in self.episode_title: 
				f245 = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")
				f490v = self.episode_title.split(":")[0].rstrip(" ")
			if f490v:
				if not "episode" in f490v.lower() and not "ep" in f490v.lower() and not f490v.lower().startswith("e"):# and not f490v.lower().startswith("E"):
					f490v = "Episode " + f490v

		if self.podcast_name in ["Dietary requirements", "History of Aotearoa New Zealand podcast", "Musician's Map", "The Frickin Dangerous Bro Show", "Dirt Church Radio"]:
			if "-" in self.episode_title:
				f245 = "-".join(self.episode_title.split("-")[1:]).lstrip(" ")
				f490v = self.episode_title.split("-")[0].rstrip(" ")
			if not f490v and self.epis_numb:
				f490v = "Episode " + self.epis_numb

		if self.podcast_name in ["On the rag" , "Papercuts" , "The real pod" , "The Offspin podcast", "Taxpayer talk","The fold"]:
			if ":" in self.episode_title:
				f245 = ":".join(self.episode_title.split(":")[1:]).lstrip(" ")

		if self.podcast_name in ["Phoenix city"]:
			if "-" in self.episode_title:
				f245 = "-".join(self.episode_title.split("-")[1:]).lstrip(" ").rstrip(" ")

		if self.podcast_name in ["Love this podcast"]:
			if "-" in self.episode_title:
				f245 = "-".join(self.episode_title.split("-")[1:]).lstrip(" ").rstrip(" ")
				f490v = self.episode_title.split("-")[0]
			if "–" in self.episode_title:
				f245 = "–".join(self.episode_title.split("-")[1:]).lstrip(" ").rstrip(" ")
				f490v = self.episode_title.split("–")[0]
		
		if self.podcast_name == "Ciaran McMeeken":
			if "//" in self.episode_title:
				f245 = ":".join(self.episode_title.split("//")[1:]).lstrip(" ")
				f490v = self.episode_title.split("//")[0].rstrip(" ")
							
		if self.podcast_name in ["Better off read"]:
			if "Ep " in self.episode_title or "Episode" in self.episode_title:
					f245 = " ".join(self.episode_title.split(" ")[2:])
					f490v = " ".join(self.episode_title.split(" ")[:2]).rstrip(":")
					f830v = f490v.lower()

		if self.podcast_name in ["The Angus Dunn Podcast Episode 5: Vika Coates, Adoption Advocate"]:
			if ":" in self.episode_title:
				f245 = self.episode_title.split(":")[-1].lstrip(" ")
				f490v = self.episode_title.split(":")[0].split("The Angus Dunn Podcast Episode")[-1].rstrip(" ").lstrip(" ")
			if "-" in self.episode_title:
				f245 = self.episode_title.split("-")[-1].lstrip(" ")
				f490v = self.episode_title.split("-")[0].split("The Angus Dunn Podcast Episode")[-1].rstrip(" ").lstrip(" ")

		if self.podcast_name in ["NZ tech podcast with Paul Spain"]:
			print("here")
			print(self.episode_title)
			if  ":" in self.episode_title and ("NZ Tech Podcast" in self.episode_title or "Episode" in self.episode_title) and not "Running time" in self.episode_title:
				ep_number = None
				print(self.episode_title)
				if ": NZ Tech Podcast" in self.episode_title:
					f245 =  ":".join(self.episode_title.split(":")[:-1])
					ep_number = re.findall(r'[0-9]+', self.episode_title.split(":")[-1])[0]
				elif "NZ Tech Podcast" in self.episode_title:
					f245 = ":".join(self.episode_title.split(":")[1:])
					try:
						ep_number = re.findall(r'[0-9]+', self.episode_title.split(":")[0])[0]
					except:
						logging.info("no episode number")
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

		if self.podcast_name in ["Indegious_Urbanism", "Alchemy","Stirring the pot", "Selfie reflective", "UC science radio", "Animal matters"]:
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

		if self.podcast_name == "Chris and Sam podcast":
			f245 = self.episode_title.split(" | ")[0]
			if  " | EP" in self.episode_title:
				f490v = "EP"+self.episode_title.split("EP")[1].split(" ")[0]

		if f490v and not f830v:
			f830v = f490v.lower()
		

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
		if self.record["100"] or self.record["110"]:
			self.record["245"].indicators =["1","0"]
		else:
			self.record["245"].indicators = ["0","0"]
		title_words =self.record["245"]["a"].split(' ')
		#print(title_words)
		if title_words[0].lower() in NON_FILING_WORDS:# or title_words[0].lower() == "at":
			#offset = len( title_words[0] ) + 1
			#print(title_words)
			if title_words[0] == "The" or title_words[0] == '“The' or title_words[0] == '"The' or title_words[0] == '"The':
				self.record["245"].indicators[1] = '4' 
			elif title_words[0] == "A" or title_words[0] == '“A' or title_words[0] == '"A'  or title_words[0] == '"A':
				self.record["245"].indicators[1] = '2'
			elif title_words[0] == "An" or title_words[0] == '“An' or title_words[0] == '"An':
				self.record["245"].indicators[1] = '3'
		
		#Field 264

		self.record["264"]["c"] = "[{}]".format(self.year)


		#Field 490

		if f490v:
			self.record["490"]["v"] = f490v
		else:
			self.record["490"]["v"] = dt.fromtimestamp(int(self.date)).strftime('%B %d, %Y')

		#Field 520
		self.description = self.description#.replace#("&nbsp;"," ")
		self.record["520"]["a"] = '"{}"--RSS feed.'.format(self.description)

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

		if self.record["830"]:
			if f830v:
				self.record["830"]["v"] = f830v + "."
			else:
				self.record["830"]["v"] = dt.fromtimestamp(int(self.date)).strftime('%B %d, %Y') + "."
		elif self.record["800"]:
			if f830v:
				self.record["800"]["v"] = f830v + "."
			else:
				self.record["800"]["v"] = dt.fromtimestamp(int(self.date)).strftime('%B %d, %Y') + "."

		elif self.record["810"]:
			if f830v:
				self.record["810"]["v"] = f830v + "."
			else:
				self.record["810"]["v"] = dt.fromtimestamp(int(date)).strftime('%B %d, %Y') + "."

		#Field 856

		my_fields = self.record.get_fields("856")
		for ind in  range(len(self.record.get_fields("856"))):
			same_field_flag = False
			subfields = self.record.get_fields("856")[ind].subfields
			indicators = self.record.get_fields('856')[ind].indicators
			if len(subfields) == 2:
				for idx in range(len(subfields)):
					if same_field_flag:
						subfields[idx] = self.harvest_link
						same_field_flag = False
					if subfields[idx] == "u":
						same_field_flag = True
				field1 = Field(tag = "856", indicators = indicators, subfields = subfields)
			elif len(subfields) > 2:
				for idx in range(len(subfields)):
					if same_field_flag:
						subfields[idx] = self.episode_link
						same_field_flag = False
					if subfields[idx] == "u":
						same_field_flag = True
				field2 = Field(tag = "856", indicators = indicators, subfields = subfields)

		self.record.remove_fields("856")
		self.record.add_ordered_field(field1)
		if self.episode_link:
			self.record.add_ordered_field(field2)

		bib_data = record_to_xml(self.record)
		bib_data = str(bib_data).replace("\\n", "\n").replace("\\", "")
		self.bib_data = start_xml + bib_data +end_xml
				

	def record_creating_routine(self, update = False, list_of_podcasts = []):


		my_db = DbHandler()
		my_dict=my_db.db_reader(
			["podcast_name", "serial_mms","rss_link","location","publish_link_to_record","episode_title","mis_mms","tags","description",
			"date","episode_link","harvest_link","date_harvested","f100","f600_first","f600_second","f600_third","f610_first",
			"f610_second","f610_third","f650_first","f650_second","f650_third","f650_forth","f655","f700_first","f700_second",
			"f700_third","f710_first","f710_second","f710_third", "template_name","tick", "epis_numb", "epis_seas"],list_of_podcasts
			)
		for epis  in my_dict:
			logging.info(epis["podcast_name"])
			if "tick" in epis.keys() and epis["tick"]:
					logging.info(epis["episode_title"])
					self.mis_mms = epis["mis_mms"]
					self.template_path = os.path.join(template_folder, epis["template_name"])
					self.year = str(dt.fromtimestamp(int(epis["date"])).strftime('%d %m %Y')).split(" ")[-1]
					self.podcast_name = epis["podcast_name"]
					self.serial_mms = epis["serial_mms"]
					self.rss_link = epis["rss_link"]
					self.location = epis["location"]
					self.publish_link_to_record = epis["publish_link_to_record"]
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
					logging.info(self.bib_data)
					my_alma = AlmaTools(self.alma_key)
					if not update:
						if not self.mis_mms:		
							my_alma.create_bib(self.bib_data)
							logging.info(my_alma.xml_response_data)
							if my_alma.status_code == 200:
								bib_grab = BeautifulSoup( my_alma.xml_response_data, 'lxml-xml' )
								try:
									self.mis_mms = bib_grab.find( 'bib' ).find( 'mms_id' ).string  
									statement = 'MMS_ID: '+self.mis_mms + " " +str(my_alma.xml_response_data)
									logging.info(statement)
									with open (os.path.join(report_folder, "mms.txt"),"a" ) as mms_file:
										mms_file.write( self.mis_mms )
										mms_file.write("\n")
								except Exception as e:
									statement =  "Could not grab mms from {}. {}".format ( my_alma.xml_response_data, str(e)  ) 
									logging.debug(statement)

					else:
						if self.mis_mms:
							print(f"Updating record {self.mis_mms}")
							print(self.bib_data)
							my_alma.update_bib(self.mis_mms, self.bib_data)
							print(my_alma.status_code)
							print(my_alma.xml_response_data)
					if self.mis_mms:
						my_db.db_update_mms (self.mis_mms, self.episode_title)

					
	
	

def main():

	my_rec = RecordCreator("prod")
	my_rec.record_creating_routine(True, ["NZ tech podcast with Paul Spain", "Phoenix city"])#,"Taxpayer talk", "The fold", "Love this podcast"])
	#my_rec.record_creating_routine(True, [])


if __name__ == '__main__':

	main()