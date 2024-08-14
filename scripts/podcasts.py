import os
import re
import io
import dateparser
import urllib3
import requests
import gspread
import shutil
import csv
from bs4 import BeautifulSoup as bs
from oauth2client import file
from time import sleep
from datetime import datetime as dt
from podcasts_database_handler import DbHandler
import sys
sys.path.insert(0, r"Y:\ndha\pre-deposit_prod\LD_working\alma_tools")
sys.path.insert(0,r"H:\secrets_and_credentials")
from alma_tools import AlmaTools
from settings import  logging, creds, podcast_sprsh, database_archived_folder, database_fullname, file_folder, report_folder, sip_folder, rosetta_folder, client_secrets_file, archived_folder, ndha_report_folder, ndha_used_report_folder, my_email_box, report_part_name, done_ies, failed_ies
from podcasts1_create_record import RecordCreator
from podcasts3_holdings_items import Holdings_items
from podcasts4_update_fields import Manage_fields
from podcasts0_harvester import harvest
from podcasts2_make_sips import sip_routine
from podcast_dict import podcasts_dict, serials

from suds.client import Client
from ros_api import a as password
#os.environ["REQUESTS_CA_BUNDLE"]=r"C:\Users\Korotesv\AppData\Roaming\Python\Python310\site-packages\certifi\cacert.pem"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Define credentials, spreadsheet and working sheet
c = gspread.authorize(creds)
gs = c.open_by_key(podcast_sprsh)
#change if the name or id of the worksheet is different
ws = gs.get_worksheet(0)

logger = logging.getLogger(__name__)


class Podcast_pipeline():

	"""
	This classs manages the entire podcast process 

	Attributes
	----------

	episode_title : str
		title of episode

	alma_key : str
		"prod" for production or "sb" for sandbox


	Methods
	-------

	insert_ies(self)
	file_cleaning(self)
	finish_existing_records_and_delete_files(self, key)
	load_spreadsheet(self)
	update_database_from_spreadsheetand_delete_row(self)
	podcast_routine(self)
	"""

		

	def __init__(self, key):

		self.alma_key = str(key)
		self.podcast_name = None

	

	def check_sip_status(self,ie):

		"""Gets ie number by sru and status by rosetta_api
		Args:
			- ie (str) - IE number, identifier for intelectual entity in Alma and Rosetta

		"""

		sru_link = r"https://ndhadeliver.natlib.govt.nz/delivery/sru?version=1.2&operation=searchRetrieve&recordPacking=xml&startRecord=0&query=IE.internalIdentifier.internalIdentifierType.PID="
		r = requests.get(sru_link+ie)
		#print(r.text)
		sip_id = re.findall(r'<dc:identifier xsi:type="SIPID">(.*?)</dc:identifier>',r.text)[0]
		env_var = os.environ
		username = os.environ["USERNAME"]
		#wsdl_url = 'https://wlguatoprilb.natlib.govt.nz/dpsws/repository/SipWebServices?wsdl'
		wsdl_url = "https://wlgprdoprilb.natlib.govt.nz/dpsws/repository/SipWebServices?wsdl"
		client = Client(wsdl_url)
		#print(dir(client.service))
		credentials = {'Username': username, 'Password': password}
		client.set_options(soapheaders=credentials)
		response = client.service.getSipStatus(sip_id)
		sip_status = re.findall(r"<status>(.*?)</status>",str(response))[0]
		if sip_status == "finished":
			return True
		quit()

	

	

	def insert_ies(self):
		
		""" Requests mms_id list from db, passes them to Alma_Tools, parses list of representation xml to extract ies, inserts  them to podcasts.db """
		
		mms_dict = {}
		my_alma = AlmaTools("prod")
		mms_dict = self.db_handler.db_reader(["mis_mms", "episode_title", "episode_id", "ie_num","serial_mms", "podcast_name"],None,True)

		for mm in mms_dict:
			if mm != {}:
				ies_list = []
				episode_id = None
				mms = None
				if "mis_mms" in mm.keys():
					mms = mm["mis_mms"]
					ie_num = mm["ie_num"]
					episode_id = mm["episode_id"]
				else:
					mms = None
					ie_num = None
									
				if mms and not ie_num:
					my_alma.get_representations(mms)
					rep_grab = bs(my_alma.xml_response_data, 'lxml-xml' )
					reps = rep_grab.find( 'representations' ).find_all('id' )
					ies = rep_grab.find_all( 'originating_record_id' )
					if len(ies) != 0:
						for ie in ies:
							ies_list.append("IE"+ie.string.split("IE")[-1])
							logger.info("IE for db: " + ies_list[0])
							if self.check_sip_status(ies_list[0]):
								logger.info("Processed.")
								self.db_handler.db_update_ie(ies_list[0],mm["episode_id"])
							else:
								logger.error("Check if the SIP {} was processed well through Rosetta".format(mms))
								quit()

				elif not mms and mm["serial_mms"] in serials and "ie_num" in mm.keys():
					if not mm["ie_num"]:
						mms=mm["serial_mms"]
						my_title_parsed =  re.sub(mm["podcast_name"].lower(), "", mm["episode_title"].lower())
						logger.debug(my_title_parsed)
						my_title_date = dateparser.parse( my_title_parsed,settings={'DATE_ORDER': 'DMY'})
						logger.info(my_title_date)
						my_alma.get_representations(mms,{"limit":"100"})
						total_count = re.findall(r'count="(.*?)">',my_alma.xml_response_data)[0]
						for i in range((int(total_count)//100)+2):
							my_alma.get_representations(mms,{"limit":"100","offset":99*i})
							repres = re.findall(r"<id>(.*?)</id>",my_alma.xml_response_data)
							for rep in repres:
								my_alma.get_representation (mms, rep)
								ie = re.findall(r"pubam:(.*?)</",my_alma.xml_response_data)[0]
								year = re.findall(r"year>(.*?)</year",my_alma.xml_response_data)[0]
								label = re.findall(r"label>(.*?)</label",my_alma.xml_response_data)[0]
								#print(label)
								my_label_date = dateparser.parse(label,settings={'DATE_ORDER': 'YMD'})
								if my_title_date  == my_label_date:
									self.db_handler.db_update_ie(ie,mm["episode_id"])
									print("IE updated in db")




	def file_cleaning(self):

		"""Deletes files which were replaced in file folders during multirun of downloading process and not in database"""
		
		#contains dictionaries of filepaths in db
		file_dictionary = self.db_handler.db_reader(["filepath"],None,True)
		#list of files to delete
		file_list_to_delete = []
		#list of all filepaths in db
		filepath_in_db_list = ["\\".join(el["filepath"].split("\\")[-2:]) for el in file_dictionary if el !={}]
		#file_folder=r"Y:\ndha\pre-deposit_prod\LD_proj\podcasts\files"
		for root, dirs, files in os.walk(file_folder):
			for name in files:
				fl_path = os.path.join(root, name)
				if "\\".join(fl_path.split("\\")[-2:]) not in filepath_in_db_list:
					file_list_to_delete.append(fl_path)
		[os.remove(del_fl) for del_fl in file_list_to_delete]
		logger.info("Files deleted during cleaning")
		logger.info(file_list_to_delete)

	def finish_existing_records_and_delete_files(self, key):

		"""
		Managing process of checking if digital representation available to run holdings and items creating module. Runs update fields module to update records with 942 field and delete duplicated fields. 
		Writes podcast_name, episode_title, bib_title, bib_numbering, mis_mms, holdings, item, ie_num, filepath, updated status to report.
		Deletes file from file folder, the sip from project sip folder and sip from rosetta_folder 

		Args:
    		- key (str): "prod" for production or "sb" for sandbox.

		"""

		my_item = Holdings_items(key)
		my_item.item_routine()
		my_alma_record = Manage_fields(key)
		my_alma_record.cleaning_routine()
		print("Removing files from report folder and Rosetta folder")
		report_filename = "report_{}.txt".format(dt.now().strftime("%Y-%m-%d_%H"))
		report_full_filename= os.path.join(report_folder,report_filename)	 		
		report_dictionary = self.db_handler.db_reader(["podcast_name","serial_mms","episode_title", "bib_title","bib_numbering", "mis_mms","holdings","item","ie_num","filepath", "updated"],None,True)
		for epis in report_dictionary:
			if epis != {} and "item" in epis.keys():
				if (epis["item"] and epis["ie_num"] and epis["updated"]) or (epis["item"] and epis["ie_num"] and epis["serial_mms"] in serials):
					if epis["serial_mms"] in serials:
						met_filename = epis["episode_title"].replace(" ","_").replace('"',"") + ".xml"
						sip_title = epis["episode_title"]
					else:
						met_filename = epis["mis_mms"] + ".xml"
						sip_title = epis["mis_mms"]
					with io.open(report_full_filename, mode="a", encoding="utf-8") as f:
					    f.write(
					        (epis.get("podcast_name", "") or "") + "|"
					        + (epis.get("episode_title", "") or "") + "|"
					        + (epis.get("bib_title", "") or "") + "|"
					        + (epis.get("bib_numbering", "") or "") + "|"
					        + str(epis.get("mis_mms", "")) + "|"
					        + str(epis.get("holdings", "")) + "|"
					        + str(epis.get("item", "")) + "|"
					        + str(epis.get("ie_num", "")) + "|"
					        + str(epis.get("updated", ""))
					        + "\n"
					    )

					try:
						os.remove(epis["filepath"])
					except FileNotFoundError as e:
						logger.debug(str(e))
					try:
					 	shutil.rmtree(os.path.join(sip_folder, epis["serial_mms"],"content","streams", sip_title ))
					except FileNotFoundError as e:
					 	logger.debug(str(e))
					try:
					 	os.remove(os.path.join(sip_folder, epis["serial_mms"],"content","streams", epis["filepath"].split("\\")[-1] ))
					except FileNotFoundError as e:
					 	logger.debug(str(e))
					try:
					 	os.remove(os.path.join(sip_folder, epis["serial_mms"],"content",sip_title+".xml" ))
					except FileNotFoundError as e:
					 	logger.debug(str(e))
					try:
					 	os.remove(os.path.join(sip_folder, epis["serial_mms"],"content",met_filename ))
					except FileNotFoundError as e:
					 	logger.debug(str(e))
					try:
					 	os.remove(os.path.join(sip_folder, epis["serial_mms"],"content","dc.xml" ))
					except FileNotFoundError as e:
					 	logger.debug(str(e))
					try:
					 	shutil.rmtree(os.path.join(rosetta_folder, epis["serial_mms"],"content","streams", sip_title ))
					except FileNotFoundError as e:
						logger.debug(str(e))
					try:
					 	os.remove(os.path.join(rosetta_folder, epis["serial_mms"],"content","streams", met_filename ))
					except FileNotFoundError as e:
						logger.debug(str(e))
					try:
					 	os.remove(os.path.join(rosetta_folder, epis["serial_mms"],"content", sip_title+".xml" ))
					except FileNotFoundError as e:
						logger.debug(str(e))
					try:
					 	os.remove(os.path.join(rosetta_folder, epis["serial_mms"],"content", met_filename ))
					except FileNotFoundError as e:
						logger.debug(str(e))

					try:
					 	os.remove(os.path.join(rosetta_folder,epis["serial_mms"],"content", "dc.xml" ))
					except FileNotFoundError as e:
						logger.debug(str(e))
					if os.path.isfile(os.path.join(rosetta_folder,epis["serial_mms"],"done")):
						os.remove(os.path.join(rosetta_folder,epis["serial_mms"],"done"))
					if os.path.isdir(os.path.join(rosetta_folder, epis["serial_mms"],"content","streams")):
						if os.listdir(os.path.join(rosetta_folder, epis["serial_mms"],"content","streams")) == []:
							shutil.rmtree(os.path.join(rosetta_folder, epis["serial_mms"],"content","streams"))
							logger.info("SIP folder removed - {}".format(os.path.join(rosetta_folder, epis["serial_mms"],"content","streams")))
					if os.path.isdir(os.path.join(rosetta_folder, epis["serial_mms"],"content",)):
						if os.listdir(os.path.join(rosetta_folder, epis["serial_mms"],"content")) == []:
							shutil.rmtree(os.path.join(rosetta_folder, epis["serial_mms"],"content"))
							logger.info("SIP folder removed - {}".format(os.path.join(rosetta_folder, epis["serial_mms"],"content")))
					for fold in os.listdir(rosetta_folder):
						fold_path = os.path.join(rosetta_folder, fold)
						if len(os.listdir(fold_path)) == 1:
							if os.listdir(fold_path)[0] == "error":
								os.remove(os.path.join(fold_path,"error"))
						if len(os.listdir(fold_path)) == 0:
							os.rmdir(fold_path)


				


	def load_spreadsheet(self):

		"""Reload the google spreadsheet
		Returns:
			ws (obj) - google working sheet object

		"""


		store = file.Storage(client_secrets_file)
		creds = store.get()
		c = gspread.authorize(creds)
		end_flag = False
		gs = c.open_by_key(podcast_sprsh)
		ws = gs.get_worksheet(0)

		return ws

	def delete_row_write_to_log(self, my_row_numb, my_row):
	    """
	    Delete a row from the spreadsheet and write the deleted row to a log file.

	    Args:
	    - my_row_numb (int): The row number to delete.
	    - my_row (list): The row data to write to the log file.

	    Returns:
	    - bool: True if the row was deleted and logged successfully, False otherwise.
	    """
	    try:
	        ws.delete_row(my_row_numb)
	        logger.info("Deleted from spreadsheet")
	        try:
	            with open(os.path.join(report_folder, "deleted_rows_log.csv"), "a", newline='', encoding="utf-8") as csv_file:
	                csv_writer = csv.writer(csv_file)
	                csv_writer.writerow(my_row)
	        except:
	            print("Could not write to deleted_rows_log.csv")
	            print(my_row)

	        return True
	    except Exception as e:
	        logger.warning(str(e))
	        return False




	def update_database_from_spreadsheetand_delete_row(self):

		"""Updates database with spreadsheet information and deletes done rows"""

		logger.info("Updating spreadsheet")
		ws = self.load_spreadsheet()
		start_point = 0
		logger.info(ws.row_count)
		end_point = ws.row_count-1
		my_row_numb = 1
		for ind  in range(start_point, end_point):
				logger.info(ind)
				my_row_numb = my_row_numb+1
				logger.info("row number {}".format(my_row_numb))
				try:
					my_row = ws.row_values(my_row_numb)
					sleep(1)
					logger.info([my_row[0],my_row[1],my_row[3]])

				except Exception as e:
					logger.warning(str(e))
					logger.info("Waiting for 50 seconds")
					sleep(50)
					ws = self.load_spreadsheet()
					my_row = ws.row_values(my_row_numb)
					logger.info(my_row)
				podcast_name = my_row[0].lstrip(" ").rstrip(" ")
				episode_title = my_row[3].lstrip(" ").rstrip(" ")
				bib_title = my_row[4].lstrip(' ').rstrip(" ")
				bib_numbering = my_row[5].lstrip(" ").rstrip(" ")
				epis_link = my_row[9].lstrip(" ").rstrip(" ")
				description = my_row[8]
				if description:
					description = description.lstrip(" ").rstrip(" ")
				f600_first = my_row[14]
				if f600_first:
					f600_first = f600_first.lstrip(" ").rstrip(" ")
				f600_second =my_row[15]
				if f600_second:
					f600_second =f600_second.lstrip(" ").rstrip(" ")
				f600_third =my_row[16]
				if f600_third:
					f600_third= f600_third.lstrip(" ").rstrip(" ")
				f610_first =my_row[17]
				if f610_first:
					  f610_first =f610_first.lstrip(" ").rstrip(" ")
				f610_second =my_row[18]
				if  f610_second:
					f610_second =f610_second.lstrip(" ").rstrip(" ")
				f610_third =my_row[19]
				if f610_third:
					f610_third =f610_third.lstrip(" ").rstrip(" ")
				f650_first =my_row[20]
				if  f650_first:
					 f650_first = f650_first.lstrip(" ").rstrip(" ")
				f650_second =my_row[21]
				if  f650_second:
					 f650_second =f650_second.lstrip(" ").rstrip(" ")
				f650_third =my_row[22]
				if f650_third:
				  f650_third = f650_third.lstrip(" ").rstrip(" ")
				f650_forth = my_row[23]
				if f650_forth:
					f650_forth = f650_forth.lstrip(" ").rstrip(" ")
				f655_first = my_row[24]
				if f655_first:
					f655_first = f655_first.lstrip(" ").rstrip(" ")
				f700_first =my_row[25]
				if f700_first:
					f700_first =f700_first.lstrip(" ").rstrip(" ")
				f700_second =my_row[26]
				if f700_second:
					f700_second =f700_second.lstrip(" ").rstrip(" ")
				f700_third =my_row[27]
				if f700_third:
					f700_third =f700_third.lstrip(" ").rstrip(" ")
				f710_first =my_row[28]
				if f710_first:
					f710_first =f710_first.lstrip(" ").rstrip(" ")
				f710_second =my_row[29]
				if f710_second:
					 f710_second = f710_second.lstrip(" ").rstrip(" ")
				f710_third =my_row[30]
				if f710_third:
					f710_third =f710_third.lstrip(" ").rstrip(" ")
				tick = my_row[31]
				try:
					cataloguer = my_row[32]
				except IndexError:
					cataloguer = None

				if tick == "TRUE":
					logger.info(f"{episode_title} is ready")
					self.db_handler.update_from_spreadsheet(
						podcast_name,
					    episode_title,
					    bib_title,
					    bib_numbering,
					    description,
					    f600_first,
					    f600_second,
					    f600_third,
					    f610_first,
					    f610_second,
					    f610_third,
					    f650_first,
					    f650_second,
					    f650_third,
					    f650_forth,
					    f655_first,
					    f700_first,
					    f700_second,
					    f700_third,
					    f710_first,
					    f710_second,
					    f710_third,
					    tick,
					    cataloguer
					)
					logger.info("Updated in db")
					sleep(1)
					gs_flag = False
					for trial in range(4):
						if not gs_flag:
							gs_flag = self.delete_row_write_to_log(my_row_numb, my_row)
							if gs_flag:
								# to remove deleted row from count
								my_row_numb = my_row_numb-1
					if not gs_flag:
						quit()





	def podcast_routine(self):

		# """The main function which manages all the processes in Podcast pipline:
		# 	1. Copies db with current date in title
		# 	2. Deletes all the files which are not in db
		# 	3. Reading emails to identify NDHA report and reading the ie numbers of finished episodes which have digital representation to list
		# 	4. Inserting ie from Alma to db checking it also in NDHA report_folder
		# 	5. Finishing existing records and deleting files
		# 	6. Updating the last issue in db for each podcast (to start harvest from it)
		# 	7. Updating database from spreadsheet and deleting row
		# 	8. Creating records for previously harvested files
		# 	9. Creating sip packages
		# 	10. Harvesting new episodes"""



		shutil.copyfile(database_fullname, os.path.join(database_archived_folder, "podcasts_{}.db".format(dt.now().strftime("%Y-%m-%d_%H"))))
		self.db_handler = DbHandler()

		#self.file_cleaning()

		# self.insert_ies()

		# self.finish_existing_records_and_delete_files("prod")#update with 942 and make items and delete SIPs form prod (project and rosetta folder)

		# self.db_handler.delete_done_from_db()

		#self.update_database_from_spreadsheetand_delete_row() 

		# my_rec = RecordCreator(self.alma_key)
		# my_rec.record_creating_routine()

		#sip_routine() #only run Friday-Monday due to Rosetta schedulling job and speciall SIP structure (serial mms --> mis_mms)

		# # #############################################
		# harvest() #first time when episode enter db
		# self.db_handler.update_the_last_issue()
		# ###############################################
		# with open("finished.txt","w") as f:
		# 	f.write("updated "+ dt.now().strftime("%Y-%m-%d_%H"))


		 		
def main():

	podcast = Podcast_pipeline("prod")
	podcast.podcast_routine()


if __name__ == "__main__":
	main()