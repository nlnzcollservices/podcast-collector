import os
import re
import io
import peewee
import requests
import hashlib
import codecs
import gspread
import time
import dateparser
from pymarc import parse_xml_to_array,record_to_xml, Field 
from datetime import datetime as dt
from podcast_models import Podcast, Episode, File
from bs4 import BeautifulSoup
try:
	from settings import file_folder, template_folder, working_folder, report_folder, config, logging, sb_key, deleted_items
except:
	from settings_prod import file_folder, template_folder, working_folder, report_folder, config, logging, sb_key, deleted_items_holdings
from openpyxl import load_workbook
from podcast_dict import podcasts_dict
from database_handler import DbHandler
from alma_tools import AlmaTools
logger = logging.getLogger(__name__)


class Holdings_items():

	""" 
	This class contains methods for managing process of creating holding and item  records in Alma , update existing items and delete duplicates

	Attributes
	----------
	key : str
		"sb" for sandbox or  "prod" for production
	update : bool
		True for updating items, False for creating new items
	mms_list : list
		list of mms ids to process
	mms_id : str
		Alma MMS IDF
	holding_id: str
		Alma holding ID
	item_pid : str
		Alma item ID
	ie_num : str
		ie number from database
	bib_data : str
		xml of Alma bibliographic record
	podcast_name :
		name of podcast from database
	podcast_bib_name:
		name of podcast from bib record 490 field
	enum : str
		enumiration b
	date : str
		publishing date from bib revcord
	holdings_data : str
		xml from holdings request
	holding_data : str
		xml from holding template
	items_data : str
		xml response from get items request
	item_data : str
		xml from item template
	holdings_list : list
		list of holdings belonging to particular mms id
	items_list : list
		list of items belonging to particular mms id and holding id
	year : str
		year of publishing from bibliographic record



	Methods
	-------
	__init__(self, key, mms_list)
	parsing_bib_xml(self)
	parse_holding(self)
	parsing_item_data_replace_tags(self, tag_dict, item_data)
	parsing_items_data(self)
	dups_deleting_routine(self)
	item_routine(self,update = False)
	"""

	def __init__(self, key):



		self.mms_id = None
		self.bib_data = None
		self.key = key
		self.holding_data = None
		self.enum =  None
		self.ie_num = None
		self.item_data = None
		self.items_data = None
		self.holdings_list = []
		self.items_list = []
		self.year = None
		self.podcast_name = None
		self.podcast_bib_name = None
		self.date = None
		


	
	def parsing_bib_xml(self):

		"""Parses bibliographic record and extracts podcast name from 490 field, 800 or 830 field to extract subfield b for description.
		Extracts date if it is possible or eumrtation if there is no date.
		"""

		self.enum = None
		self.podcast_bib_name = None
		self.date = None
		record = parse_xml_to_array(io.StringIO(self.bib_data))[0]
		self.podcast_bib_name = record["490"]["a"].rstrip(", ")
		year = record["264"]["c"].strip("[]")
		logger.debug(year)
		self.year = dateparser.parse(year)
		if record["830"]:
			my_alma = record["830"]["v"]
		elif record["800"]:
			my_alma = record["800"]["v"]
		self.date = dateparser.parse(my_alma)

		if not self.date:
			if len(re.findall(r"(?<!\d)\d{1}(?!\d)",my_alma)) == 1:
				self.enum = re.findall(r"(?<!\d)\d{1}(?!\d)",my_alma)[0]
			elif len(re.findall(r"(?<!\d)\d{2}(?!\d)",my_alma)) == 1:
				self.enum = re.findall(r"(?<!\d)\d{2}(?!\d)",my_alma)[0]
			elif len(re.findall(r"(?<!\d)\d{3}(?!\d)",my_alma)) == 1:
				self.enum =  re.findall(r"(?<!\d)\d{3}(?!\d)",my_alma)[0]


	def parse_holding(self):

		"""Parses holding xml data to find holding numbers. Making holdings_list
		""" 

		self.holdings_list = []
		try:
			hold_grab = BeautifulSoup( self.holdings_data, 'lxml-xml' )
			self.hold_list = hold_grab.find("holdings").find_all("holding_id")
			for hold_line in self.hold_list:
				self.holdings_list.append(hold_line.text)
				logger.info(self.holdings_list)
		except Exception as e:
			logger.exception(str(e))




	def parsing_item_data_replace_tags(self, tag_dict, item_data):

		"""Replaces tags of item xml data to tags from tag dictionary
		Arguments:
			tag_dict(dict) -  tage names and new tag contant
			item_data(str) - item record xml

		Returns:
			item_data(str) - new item record xml
		"""

		for el in tag_dict.keys():
			item_data = item_data.replace(str(item_grab.find("item").find(el)), tag_dict[el])
		return item_data	    


	def parsing_items_data(self):

		"""Searching for item numbers in items xml file. Makes item_list"""

		self.items_list = []
		try:
			item_grab = BeautifulSoup( self.items_data, 'lxml-xml' )
			items_list = item_grab.find("items").find_all("item")
			for item_line in items_list:
				self.items_list.append(item_line.attrs["link"].split("/")[-1])
			logger.info(self.items_list)
		except Exception as e:
			logger.exception(str(e))

	
	def dups_deleting_routine(self, mms_list):

		"""Deleting dupped items and holdings. Leaving the last holding and the last item in the last holding"""

		logger.info("Cheking and deleting holding and item duplicates...")
		for mmsline in mms_list:
			self.mms_id = str(mmsline[0])
			logger.info(self.mms_id)
			self.item_pid = ""
			my_alma=AlmaTools(self.key)
			my_alma.get_holdings(self.mms_id)
			self.holdings_data = my_alma.xml_response_data
			self.parse_holding()
			if len(self.holdings_list) >=1:
				logger.info("The number of holdings is " +len(self.holdings_list))
				for ind in range(len(self.holdings_list)):
					#checks if this is the last holding to set minus one for keeping the last item of this holding and then to delete all other holdings.
					if ind<len(self.holdings_list)-1:
						not_last_holding=0
					else:
						not_last_holding=1
					self.holding_id = self.holdings_list[ind]
					my_alma.get_items(self.mms_id, elf.holding_id)
					self.items_data = my_alma.xml_response_data
					self.parsing_items_data()
					logger.info("Number of items is " + len(self.items_list))
					if len(self.items_list) >1:
						for idx in range(len(self.items_list)-not_last_holding):
							self.item_pid  = self.items_list[idx]
							my_alma.get_item(self.mms_id, self.holding_id, self.item_pid)
							self.item_data = my_alma.xml_response_data
							#item could not be deleted if PO_line attached to it.
							self.parsing_item_data_replace_tags({"po_line":""}, self.item_data)
							#updates item with empty po_line
							my_alma.update_item(self.mms_id, self.holding_id, self.item_pid,self.item_data)
							my_alma.delete_item(self.mms_id, self.holding_id, self.item_pid)
							logger.info("item " + self.item_pid  + " deleted")
							with open(deleted_items_holdings,"a") as fl:
								fl.write(self.item_pid)
								fl.write("\n")
					if not_last_holding ==0:
						my_alma.delete_holding(self.mms_id, self.holding_id)
						logger.info("holding " + self.holding_id + " deleted")
						with open(deleted_items_holdings,"a") as fl:
							fl.write(self.item_pid)
							fl.write("\n")	

			else:
				print("No holdings")
					

	

	def item_routine(self, mms_list=[], update = False):

		"""Checking existing item and holding and creates where do not exists. Checks Alma bibliographic record for 890 field to identify correct enueration and chronology field and make a description
		Raises:
			Quit if duplicate holding or items

		"""
		
		self.mms_list = mms_list
		self.update = update
		for pod_list  in  self.mms_list:
			if pod_list and pod_list[0] != None:
				self.holding_data = None
				self.item_data = None
				self.items_data = None
				self.bib_data = None
				self.holdings_list = []
				self.items_list = []
				self.holdings_list = []
				self.holding_id = pod_list[1]
				self.item_pid  = pod_list[2]
				self.ie_num = pod_list[3]

				if len(pod_list)>4:
					self.podcast_name = pod_list[4]
				else:
					self.podcast_name = None
				logger.info(self.podcast_name)
				self.mms_id = pod_list[0]
				logger.info(self.mms_id)
				db_handler = DbHandler()
				my_alma = AlmaTools(self.key)
				my_alma.get_bib( self.mms_id)
				self.bib_data= my_alma.xml_response_data
				logger.info(self.bib_data)
				self.parsing_bib_xml()
				if "/" in self.podcast_bib_name:
					self.podcast_name =  self.podcast_bib_name.split("/")[0].rstrip(" ")
				if not self.podcast_name:
					self.podcast_name = self.podcast_bib_name.replace("-","").replace(":","").replace("/","").replace('  ', " ")
				if self.podcast_name == "Just being me no apology":
					self.podcast_name ="Just me being me no apology"
				if self.ie_num:
					if self.mms_id:
						with open(os.path.join(template_folder, "holding.xml")) as hold_data:
							self.holding_data = hold_data.read()
						my_alma.get_holdings(self.mms_id,{"limit":"100"})
						self.holdings_data = my_alma.xml_response_data
						self.parse_holding()
						self.serial_pol = podcasts_dict[self.podcast_name]["serial_pol"]
						if self.holdings_list != []:
							if len(self.holdings_list) >1:
								logger.warning("Holding duplicates")
								logger.warning(self.holdings_list)
								self.dups_deleting_routine([[self.mms_id]])
							else:
								if not self.holding_id or self.holding_id != self.holdings_list[0]:
									db_handler.db_update_holding(self.mms_id, self.holdings_list[0])
									self.holding_id = self.holdings_list[0]
						if not self.holding_id and self.mms_id:
							logger.info('Creating holdings')
							my_alma.create_holding(self.mms_id, self.holding_data)
							holding_grab = BeautifulSoup( my_alma.xml_response_data, 'lxml-xml' )
							self.holding_id= holding_grab.find( 'holding' ).find( 'holding_id' ).string
							logger.info(self.holding_id)
							db_handler.db_update_holding(self.mms_id, self.holding_id)

						my_alma.get_items(self.mms_id, self.holding_id)
						self.items_data = my_alma.xml_response_data
						self.parsing_items_data()
						if self.items_list != []:
							if len(self.items_list) >1:
								logger.warning("Item duplicates")
								logger.warning(self.items_list)
								self.dups_deleting_routine([[self.mms_id]])
							else:
								if not self.item_pid or self.item_pid != self.items_list[0]:
									self.item_pid = self.items_list[0]
									db_handler.db_update_item_id(self.mms_id, self.items_list[0])
						if (not self.item_pid  and self.holding_id and self.mms_id) or (self.item_pid and self.update) :

								polstring = "<po_line>{}</po_line>".format(self.serial_pol)
								if  self.enum:
									chron_j = ""
									chron_k = ""
									chron_i = dt.strftime(self.year, "%Y")
									description = "<description>no. {} ({})</description>)".format(self.enum, chron_i)
									enum = self.enum
								else:
									enum = ""
									if self.date:
										chron_j = dt.strftime(self.date,"%m")
										chron_k = dt.strftime(self.date,"%d")
										chron_i = dt.strftime(self.date,"%Y")
									else:
										chron_j = ""
										chron_k = ""
										chron_i = dt.strftime(self.year,"%Y")
									description = "<description>{} {} {}</description>".format( chron_i, chron_j,chron_k)
								chron_i_stat = "<chronology_i>{}</chronology_i>".format( chron_i )
								chron_j_stat = "<chronology_j>{}</chronology_j>".format( chron_j )
								chron_k_stat = "<chronology_k>{}</chronology_k>".format( chron_k )
								enum_stat = "<enumeration_b>{}</enumeration_b>".format( enum )
								time_substitute_statement = "<creation_date>{}</creation_date>".format(str(dt.now().strftime( '%Y-%m-%d')))
								receiving_stat = "<arrival_date>{}</arrival_date>".format(str(dt.now().strftime( '%Y-%m-%d')))
								with open(os.path.join(working_folder,"assets", "templates","item.xml"), "r") as data:
									item_data = data.read()
									item_data = item_data.replace("<creation_date></creation_date>", time_substitute_statement)
									item_data = item_data.replace("<po_line></po_line>", polstring )
									item_data = item_data.replace("<enumeration_b></enumeration_b>", enum_stat )
									item_data = item_data.replace("<chronology_i></chronology_i>", chron_i_stat )
									item_data = item_data.replace("<chronology_j></chronology_j>", chron_j_stat )
									item_data = item_data.replace("<chronology_k></chronology_k>", chron_k_stat )
									item_data = item_data.replace("<description></description>", description )
									item_data = item_data.replace("<arrival_date></arrival_date>", receiving_stat )
								self.item_data = item_data
								if not self.update:
									logger.info("Creating item")
									my_alma.create_item(self.mms_id, self.holding_id,self.item_data)
									logger.debug(my_alma.xml_response_data)
									logger.debug(my_alma.status_code)
									item_grab = BeautifulSoup(my_alma.xml_response_data, "lxml-xml")
									self.item_pid  = item_grab.find('item').find( 'item_data' ).find( 'pid' ).string 
									logger.info(self.item_pid + " - item created")
									db_handler.db_update_item_id(self.mms_id, self.item_pid)
									
								else:
									logger.info("Updating item")
									logger.info(self.item_pid)
									my_alma.get_item(self.mms_id, self.holding_id, self.item_pid)
									self.item_data= self.parsing_item_data_replace_tags({"description":description, "chronology_i":chron_i_stat, "chronology_j":chron_j_stat, "chronology_k":chron_k_stat, "enumeration_b":enum_stat}, my_alma.xml_response_data)
									my_alma.update_item(self.mms_id, self.holding_id, self.item_pid, self.item_data)
									logger.debug(my_alma.xml_response_data)
									logger.debug(my_alma.status_code)
									logger.info(self.item_pid +" - item updated")

								report_name = "report"+str(dt.now().strftime("_%d%m%Y_%H_%M"))+".txt"

								with open(os.path.join(report_folder, report_name),"a") as f:
									f.write("{}|{}|{}|{}".format(self.mms_id, self.holding_id, self.item_pid, self.ie_num))
									f.write("\n")		

def main():

	"""Runs all the process starting with mms_list. If mms_list does_not exists it takes information from database. Creates episode_list and pass it to 
	deleting duplicates and item routine function.
	Deleting duplicates is optional and can be commented.
	update should be set True if records are going to be updated and False if not. It is False by default""" 
	update = True
	episode_list = []
	mms_list = []
	for mms in mms_list:
		episode_list.append([mms, None, None, True])
	if len(mms_list)==0:
		my_podcasts = DbHandler().db_reader(["podcast_name", "mis_mms", "holdings", "item","ie_num"], None, True)
	if len(episode_list)==0:
		episode_list = [[el["mis_mms"],el["holdings"],el["item"],el["ie_num"],el["podcast_name"]] for el in my_podcasts if "mis_mms" in el.keys()]
		if mms_list == []:
			mms_list = episode_list
		
	my_item = Holdings_items("prod")
	my_item.mms_list = mms_list
	#my_item.dups_deleting_routine(mms_list)
	my_item.item_routine(mms_list)
			



if __name__ == '__main__':

	
	main()