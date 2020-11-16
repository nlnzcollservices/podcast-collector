import os
import io
import requests
import hashlib
import gspread
from pymarc import parse_xml_to_array,record_to_xml, Field 
import time
from bs4 import BeautifulSoup
from datetime import datetime as dt
try:
	from settings import logging, file_folder, template_folder, pr_key, sb_key, logging, start_xml, end_xml
except:
	from settings_prod import logging, file_folder, template_folder, pr_key, sb_key, logging, start_xml, end_xml
from openpyxl import load_workbook
from alma_tools import AlmaTools
from database_handler import DbHandler
logger = logging.getLogger(__name__)

class Manage_fields():

	"""
	Attributes
	----------

	This class updates bibliographic record in Alma

	f347 : pymarc.Field object
		347 field 
	f500 : pymarc.Field object
		500 field
	f856 : pymarc.Field object
		856 field 
	f942 : pymarc.Field object
		942 field 
	key : str
		"prod" for production or "sb" for sandbox
	mms_id : str
		Alma mms id of bibliographic record
	mms_id_list : str
		list which contains mms ids.
	duplicate_flag : bool
		flag set False but default and become true if the field is duplicated
	update_flag: bool
		flag set False by default and becomve True if 942 added and record has to be updated

	Methods
	-------
	def __init__(self, key, mms_id_list)		
	def removing_dup_fields_add_942(self, field_num)
	def parsing_bib_xml(self)
	def cleaning_routine(self)

	"""



	def __init__(self, key,):

		self.f347 = None
		self.f500 = None
		self.f856 = None
		self.f942 = None
		self.key = key
		self.alma_key = None
		self.mms_id = None
		self.flag = False

		
			
	def removing_dup_fields_add_942(self, field_num):

		"""
		Using pymarc object for finding and removing particular duplicate field
		Parameters:
			field_num(str) - number of field

		"""
		
		fields = self.record.get_fields(field_num)
		print(len(fields))
		print(field_num)
		print(self.record)
		if len(fields) != 0:
			field_dict = {}
			for ind in range(len(fields)):
				if fields[ind].value() not in field_dict:
					field_dict[fields[ind].value()] = [fields[ind]]
				else:
					field_dict[fields[ind].value()] += [fields[ind]]
					self.duplicate_flag = True

			if self.duplicate_flag:
				logger.info(field_num - "duplicated")
				self.record.remove_fields(field_num)
				for el in field_dict.keys():
					self.record.add_ordered_field(field_dict[el][0])
				logger.info("removed")


		else:
			if field_num == "942":
				date_942 = 	(str(dt.now().strftime( '%Y-%m')))
				f942 = Field(tag = '942', indicators = ["",""], subfields = ['a', 'nznb {}'.format(date_942)])
				self.record.add_ordered_field(f942)
				logger.info("record updated with 942")
				self.update_flag = True
						



	def parsing_bib_xml(self):

		""""Converts bib xml to pymarc. Looking for duplicates in self.field_list. Runs removing_dup_fields_add_942"""

		self.record = parse_xml_to_array(io.StringIO(self.bib_data))[0]
		self.field_list = ["347", "500", "856", "942"]
		for field_num in self.field_list:
			self.removing_dup_fields_add_942(field_num)
		self.bib_data =start_xml+str(record_to_xml(self.record)).replace("\\n", "\n").replace("\\", "")+end_xml
		logger.debug(self.bib_data)

	def cleaning_routine(self, mms_id_list):

		"""
		Running routine for modification of bib record
		Parameters:
			mms_id_list(list) - list with mms_id record for which items already were created

		"""
		self.mms_id_list = mms_id_list
		logger.info("Updating records with 942 and removeing duplicated fields")
		sb_mms = None
		if self.key=="sb":
			sb_mms = "9918602951502836"
		self.f347 = None
		self.f500 = None
		self.f856 = None
		self.f942 = None
		self.mms_id = None
		self.bib_data = None
		for mms in self.mms_id_list:
				self.duplicate_flag = False
				self.update_flag = False
				self.mms_id = mms
				logger.info(self.mms_id)
				my_rec = AlmaTools(self.key)
				my_rec.get_bib(self.mms_id)
				self.bib_data = my_rec.xml_response_data
				self.parsing_bib_xml()
				print(self.update_flag)
				if self.update_flag:
					my_rec.update_bib(self.mms_id, self.bib_data)
					print(my_rec.status_code)
					logger.info(self.mms_id + " - updated")
					my_db =DbHandler()
					my_db.db_update_updated(self.mms_id)
				else:
					logger.info("Already has 942 field")





def main():


	mms_list = []

	# workook_path = r"D:\\dup_942.xlsx"
	# if os.path.exists(workook_path):

	# 	wb = load_workbook(workook_path)
	# 	#Enter name of the working sheet below
	# 	ws= wb.get_sheet_by_name("results")
	# 	#if now headers min_row =1
	# 	for row in ws.iter_rows(min_row=2):

	# 	#depending on where mms id is row[3] should be changed to number of column started from 0.
	# 		mms = row[21].value
	# 		mms_list.append(row[21].value)


	
	db_handler = DbHandler()
	my_episodes = db_handler.db_reader(["podcast_name", "mis_mms", "holdings", "item","ie_num"], None, True)
	for episode in my_episodes:
		if "mis_mms" in episode.keys():
			if episode["item"]:
				mms_list.append(episode["mis_mms"])


	my_rec = Manage_fields("prod")
	my_rec.cleaning_routine(mms_list)
		

if __name__ == '__main__':

	
	main()