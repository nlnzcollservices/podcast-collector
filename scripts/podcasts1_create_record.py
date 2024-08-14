import os
import io
from pymarc import parse_xml_to_array,record_to_xml, Field, Subfield, MARCWriter

from bs4 import BeautifulSoup
from datetime import datetime as dt
from settings import logging, template_folder,start_xml, end_xml, report_folder, marc_folder

from podcasts_database_handler import DbHandler
import dateparser
from podcast_dict import serials
import sys
sys.path.insert(0, r"Y:\ndha\pre-deposit_prod\LD_working\alma_tools")
from alma_tools import AlmaTools
logger = logging.getLogger(__name__)
# logger.setLevel('DEBUG')

def export_marc_record(marc_record, mms_id, export_folder):
    """
    Exports a MARC record to a file.

    Parameters:
    - marc_record: pymarc Record object.
    - mms_id: str, the MMS ID of the record.
    - export_folder: str, the folder where the MARC file will be saved.

    The filename is formatted as yyyy_mm_dd_mms_id.mrc
    """
    date_str = dt.now().strftime("%Y_%m_%d")
    filename = f"{date_str}_{mms_id}.mrc"
    filepath = os.path.join(export_folder, filename)
    with open(filepath, 'wb') as file_out:
        writer = MARCWriter(file_out)
        writer.write(marc_record)
        writer.close()
    print(f"Record exported as {filename}")

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
		self.episode_numbering = None
		self.episode_title = None
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
		#print(my_record_xml)
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

	
		
		#Field 245

		#print(self.bib_title)

		self.record["245"]["a"] = self.bib_title


	#################################################################################		

		self.record["245"].indicators = ["0","0"]

	##########################################################################3

		title_words =self.record["245"]["a"].split(' ')

		if title_words[0].lower() in NON_FILING_WORDS:

			if title_words[0] in ["The",'“An','"An']:
				self.record["245"].indicators[1] = '4' 
			elif title_words[0] == "A" or title_words[0]:
				self.record["245"].indicators[1] = '2'
			elif title_words[0] in ["An",'“A','"A',"'A"]:
				self.record["245"].indicators[1] = '3'
			elif title_words[0] in ['“The','"The', "'The"]:
				self.record["245"].indicators[1] = '5'
		
		#Field 264

		self.record["264"]["c"] = "[{}]".format(self.year)


		#Field 490

		try:
			my_date = dt.fromtimestamp(int(self.date)).strftime('%B %d, %Y')
		except ValueError:
			my_date = dateparser.parse(self.date).strftime('%B %d, %Y')
		try:
			self.record["490"]["v"] = dt.fromtimestamp(int(self.date)).strftime('%B %d, %Y')
		except ValueError:
			self.record["490"]["v"]= my_date

		#Field 520

		#First 520 field
		self.description = self.description#.replace#("&nbsp;"," ")
		try:
			self.record["520"]["a"] = '"{}"--RSS feed.'.format(self.description)
		except:
			logger.debug("No description")

		#Second 520 field

		if self.bib_numbering:
			if self.bib_numbering != "":
				f520_2 = Field(
					        tag='520',
					        indicators=['', ''],
					        subfields=[Subfield(code='a', value=self.bib_numbering)]
					    )
				self.record.add_ordered_field(f520_2)



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
			self.record["830"]["v"] = my_date + "."
		elif "800" in self.record:
			self.record["800"]["v"] = my_date + "."

		elif "830" in self.record:
			self.record["810"]["v"] = my_date + "."

		#Field 856
		
		my_fields = self.record.get_fields("856")
		if len(my_fields) !=0:
			for ind in  range(len(self.record.get_fields("856"))):
				ndha_archived_flag=False
				subfields = self.record.get_fields("856")[ind].subfields
				indicators = self.record.get_fields('856')[ind].indicators
				#For updates to exlude automated field
				for sld in subfields:
					if sld.code == "z":
						idha_archived_flag = True
				if not ndha_archived_flag:
					# print(subfields)
					# print(len(subfields))
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
			#print(self.record)
		#print("HERE")
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
			["podcast_name", "podcast_id", "serial_mms","rss_link","location","publish_link_to_record","episode_title", "bib_title",
			"bib_numbering","mis_mms","ie_num","tags","description", "date","episode_link","harvest_link","date_harvested",
			"f600_first","f600_second","f600_third","f610_first", "f610_second","f610_third","f650_first",
			"f650_second","f650_third","f650_forth","f655","f700_first","f700_second", "f700_third","f710_first",
			"f710_second","f710_third", "template_name","tick", "epis_numb", "epis_seas"],list_of_podcasts
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
					self.bib_numbering = epis["bib_numbering"]
					self.bib_title = epis["bib_title"]
					self.tags = epis["tags"]
					self.description = epis["description"]
					self.date = epis["date"]
					self.episode_link = epis["episode_link"]
					self.harvest_link = epis["harvest_link"]
					self.date_harvested = epis["date_harvested"]
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
									export_marc_record(self.record, self.mms_id, marc_folder)
									with open (os.path.join(report_folder, "mms.txt"),"a" ) as mms_file:
										mms_file.write( self.mms_id )
										mms_file.write("\n")
									with io.open(os.path.join(report_folder,"mms_titles.txt"),"a", encoding="utf-8") as mms_title_file:
										mms_title_file.write("{}|{}".format(self.mms_id, self.episode_title))
										mms_title_file.write("\n")
								except Exception as e:
									print(str(e))
									statement =  "Could not grab mms from {}. {}".format ( my_alma.xml_response_data, str(e)  ) 
									logger.error(statement)
									quit()


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
	my_rec.record_creating_routine(True, ["The real pod"])#,"Taxpayer talk", "The fold"])
	#my_rec.record_creating_routine(True, [])


if __name__ == '__main__':

	main()