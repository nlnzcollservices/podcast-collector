import os
import re
import io

import gspread
import shutil
from bs4 import BeautifulSoup as bs
from oauth2client import file
from time import sleep
from datetime import datetime as dt
from database_handler import DbHandler
import sys
sys.path.insert(0, r"Y:\ndha\pre-deposit_prod\LD_working\alma_tools")
from alma_tools import AlmaTools
try:
	from settings_prod import  logging, creds, podcast_sprsh, database_archived_folder, database_fullname, file_folder, report_folder, sip_folder, rosetta_folder, client_secrets_file, archived_folder, ndha_report_folder, ndha_used_report_folder, my_email_box, report_part_name, done_ies, failed_ies
except:
	from settings import  logging, creds, podcast_spsrsh, database_archived_folder, database_fullname, file_folder, report_folder, sip_folder, rosetta_folder, client_secrets_file, archived_folder, ndha_report_folder, ndha_used_report_folder, my_email_box, report_part_name, done_ies, failed_ies
from podcasts1_create_record import RecordCreator
from podcasts3_holdings_items import Holdings_items
from podcasts4_update_fields import Manage_fields
from podcasts0_harvester import harvest
from podcasts2_make_sips import sip_routine
from podcast_dict import podcasts_dict, serials
import csv
import win32com.client
import os
import datetime
import itertools
import dateparser
import urllib3
import  sys

#os.environ["REQUESTS_CA_BUNDLE"]=r"C:\Users\Korotesv\AppData\Roaming\Python\Python310\site-packages\certifi\cacert.pem"
#os.environ["REQUESTS_CA_BUNDLE"]=r"C:\Users\Korotesv\AppData\Roaming\Python\Python39\site-packages\certifi\cacert.pem"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
	email_downloader(self)
	get_ies_from_reports(self)
	read_ies_file(self)
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

	def email_downloader(self):


		'''
		Connects to the outlook, finds the correct sub folder named '45. Weekly Published' under 'Inbox' in my_email_box and downloads all of the attatchements in all of the emails 

		'''
		outlookConnection = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
		folder = outlookConnection.Folders.Item(my_email_box)
		inbox = folder.Folders.Item("Inbox")
		session = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
		message = inbox.Items
		logger.debug(len(message))
		for ms in message:
		    try:
		        my_time = str(ms.ReceivedTime).split(".")[0].replace(" ","_").replace(':','_')
		        if report_part_name in ms.subject:
		            if ms.Attachments:
		                    for attachment in ms.Attachments:
		                        try:
		                            if (str(attachment)).find('image') != -1:
		                                continue

		                            filename, file_extension = os.path.splitext(os.path.join(ndha_report_folder, attachment.FileName))
		                            if file_extension == ".csv":
			                            unique_name = "".join([filename,my_time,file_extension])
			                            if not os.path.isfile(unique_name) and not os.path.isfile(unique_name.replace(ndha_report_folder, ndha_used_report_folder)):
			                            	attachment.SaveAsFile(unique_name)
			                            	logger.info("Saved the attatchemnt " + str(unique_name))
		                        except Exception as e:
		                            logger.error(str(e))
		    except Exception as e:
		        logger.error(str(e))        


	def get_ies_from_reports(self):
		
		"""Starts email.downloader and then goes to ndha_report_folder and looking across all the reports. (All the records, which have been processed through Rosetta go to the reports which have been emailed).Writes ie numbers with "finished" status  to "done_report_ies.txt" and 
		and  to  "failed_report_ies.txt" otherwise. Moves all read files to other folder
		Raises:
			Exception - during reading report file and writing to files. Prints error.
		"""

		self.email_downloader()
		report_list = os.listdir(ndha_report_folder)
		my_dict = {}
		for report in report_list:
			logger.debug(report)
			move_flag = True
			with open(os.path.join(ndha_report_folder, report),"r", encoding = 'utf-8') as csvfile:
				reader = csv.reader(csvfile, delimiter = ",")
				try:
					next(reader)
					next(reader)
					next(reader)
					next(reader)
				except Exception as e:
					logger.error(str(e))
					logger.error(report)
					move_flag = False
				try:
					for row in reader:
						if len(row)>3:
							alma_mms_id = row[4]
							ie_num = row[3].rstrip(" ")
							status = row[8].rstrip(" ")
							# alma_mms_id = row[7]
							# ie_num = row[6].rstrip(" ")
							# status = row[14].rstrip(" ")
							if alma_mms_id != "" and ie_num != "" and status =="FINISHED":
								with open(done_ies, "a") as f:
									f.write(ie_num)
									f.write("\n")
							if alma_mms_id != "" and ie_num != "" and status != "FINISHED":
								logger.warning("Check the SIP "+alma_mms_id)
								with open(failed_ies, "a") as f:
									f.write(alma_mms_id + "|" + ie_num)
									f.write("\n")
				except Exception as e:
					logger.error(str(e))
			if move_flag:
				shutil.move(os.path.join(ndha_report_folder, report),os.path.join(ndha_used_report_folder, report))

	def read_ies_file(self):

		"""
		Opens done_ies file from report_folder. 

		Returns:
			ies_list(list) - list which contains ie numbers from NDHA report

		"""

		ies_list = []
		with open(done_ies, "r") as f:
			data = f.read()
		for el in data.split("\n")[:-1]:
			if not el in ies_list:
				ies_list.append(el)
		return ies_list

	def insert_ies(self):
		
		""" Requests mms_id list from db, passes them to Alma_Tools, parses list of representation xml to extract ies, inserts  them to podcasts.db """
		
		mms_dict = {}
		my_alma = AlmaTools("prod")
		mms_dict = self.db_handler.db_reader(["mis_mms", "episode_title", "episode_id", "ie_num","serial_mms", "podcast_name"],None,True)
		rosetta_ies_list = self.read_ies_file()
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
					#logger.info(my_alma.xml_response_data)
					rep_grab = bs(my_alma.xml_response_data, 'lxml-xml' )
					reps = rep_grab.find( 'representations' ).find_all('id' )
					ies = rep_grab.find_all( 'originating_record_id' )
					if len(ies) != 0:
						for ie in ies:
							ies_list.append("IE"+ie.string.split("IE")[-1])
							logger.info("IE for db: " + ies_list[0])
							if not ies_list[0] in rosetta_ies_list:
								print(ies_list[0])
								print(mms)
								logger.error("Check if the SIP {} was processed well through Rosetta".format(mms))
								quit()
							self.db_handler.db_update_ie(ies_list[0],mm["episode_id"])

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





					# my_alma.get_representations(mms,{"limit":"100"))
					# 					reps = rep_grab.find( 'representations' ).find_all('id' )
					# ies = rep_grab.find_all( 'originating_record_id' )



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
		Writes podcast_name, episode_title, mis_mms, holdings, item, ie_num, filepath, updated status to report.
		Deletes file from file folder, the sip from project sip folder and sip from rosetta_folder 

		"""
		my_item = Holdings_items(key)
		my_item.item_routine()
		my_alma_record = Manage_fields(key)
		my_alma_record.cleaning_routine()
		report_filename = "report_{}.txt".format(dt.now().strftime("%Y-%m-%d_%H"))
		report_full_filename= os.path.join(report_folder,report_filename)	 		
		report_dictionary = self.db_handler.db_reader(["podcast_name","serial_mms","episode_title","mis_mms","holdings","item","ie_num","filepath", "updated"],None,True)
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
						f.write(epis["podcast_name"] + "|" + epis["episode_title"]  + "|" + str(epis["mis_mms"])  + "|" + str(epis["holdings"]) + "|" + str(epis["item"]) + "|" + str(epis["ie_num"]) + "|" +str(epis["updated"])   + "\n" )
					try:
						os.remove(epis["filepath"])
					except FileNotFoundError as e:
						logger.error(str(e))
					try:
					 	shutil.rmtree(os.path.join(sip_folder, epis["serial_mms"],"content","streams", sip_title ))
					except FileNotFoundError as e:
					 	logger.error(str(e))
					try:
					 	os.remove(os.path.join(sip_folder, epis["serial_mms"],"content","streams", epis["filepath"].split("\\")[-1] ))
					except FileNotFoundError as e:
					 	logger.error(str(e))
					try:
					 	os.remove(os.path.join(sip_folder, epis["serial_mms"],"content",sip_title+".xml" ))
					except FileNotFoundError as e:
					 	logger.error(str(e))
					try:
					 	os.remove(os.path.join(sip_folder, epis["serial_mms"],"content",met_filename ))
					except FileNotFoundError as e:
					 	logger.error(str(e))
					try:
					 	os.remove(os.path.join(sip_folder, epis["serial_mms"],"content","dc.xml" ))
					except FileNotFoundError as e:
					 	logger.error(str(e))
					try:
					 	shutil.rmtree(os.path.join(rosetta_folder, epis["serial_mms"],"content","streams", sip_title ))
					except FileNotFoundError as e:
						logger.error(str(e))
					try:
					 	os.remove(os.path.join(rosetta_folder, epis["serial_mms"],"content","streams", met_filename ))
					except FileNotFoundError as e:
						logger.error(str(e))
					try:
					 	os.remove(os.path.join(rosetta_folder, epis["serial_mms"],"content", sip_title+".xml" ))
					except FileNotFoundError as e:
						logger.error(str(e))
					try:
					 	os.remove(os.path.join(rosetta_folder, epis["serial_mms"],"content", met_filename ))
					except FileNotFoundError as e:
						logger.error(str(e))
					
					#check rosetta folder 9919015065802836 - done removed 17.04 removed
					#check rosetta folder 9919014268302836 - 14.04 removed

					try:
					 	os.remove(os.path.join(rosetta_folder,epis["serial_mms"],"content", "dc.xml" ))
					except FileNotFoundError as e:
						logger.error(str(e))
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
				
				episode_title = my_row[3].lstrip(" ").rstrip(" ")
				epis_link = my_row[5].lstrip(" ").rstrip(" ")
				description = my_row[4]
				if description:
					description = description.lstrip(" ").rstrip(" ")
				f100 = my_row[9]
				if f100:
					f100 = f100.lstrip(" ").rstrip(" ")
				f600_first = my_row[10]
				if f600_first:
					f600_first = f600_first.lstrip(" ").rstrip(" ")
				f600_second =my_row[11]
				if f600_second:
					f600_second =f600_second.lstrip(" ").rstrip(" ")
				f600_third =my_row[12]
				if f600_third:
					f600_third= f600_third.lstrip(" ").rstrip(" ")
				f610_first =my_row[13]
				if f610_first:
					  f610_first =f610_first.lstrip(" ").rstrip(" ")
				f610_second =my_row[14]
				if  f610_second:
					f610_second =f610_second.lstrip(" ").rstrip(" ")
				f610_third =my_row[15]
				if f610_third:
					f610_third =f610_third.lstrip(" ").rstrip(" ")
				f650_first =my_row[16]
				if  f650_first:
					 f650_first = f650_first.lstrip(" ").rstrip(" ")
				f650_second =my_row[17]
				if  f650_second:
					 f650_second =f650_second.lstrip(" ").rstrip(" ")
				f650_third =my_row[18]
				if f650_third:
				  f650_third = f650_third.lstrip(" ").rstrip(" ")
				f650_forth = my_row[19]
				if f650_forth:
					f650_forth = f650_forth.lstrip(" ").rstrip(" ")
				f655_first = my_row[20]
				if f655_first:
					f655_first = f655_first.lstrip(" ").rstrip(" ")
				f700_first =my_row[21]
				if f700_first:
					f700_first =f700_first.lstrip(" ").rstrip(" ")
				f700_second =my_row[22]
				if f700_second:
					f700_second =f700_second.lstrip(" ").rstrip(" ")
				f700_third =my_row[23]
				if f700_third:
					f700_third =f700_third.lstrip(" ").rstrip(" ")
				f710_first =my_row[24]
				if f710_first:
					f710_first =f710_first.lstrip(" ").rstrip(" ")
				f710_second =my_row[25]
				if f710_second:
					 f710_second = f710_second.lstrip(" ").rstrip(" ")
				f710_third =my_row[26]
				if f710_third:
					f710_third =f710_third.lstrip(" ").rstrip(" ")
				tick = my_row[27]
				if tick == "TRUE":
					logger.info(f"{episode_title} is ready")
					self.db_handler.update_from_spreadsheet(episode_title, description, f100, f600_first, f600_second, f600_third, f610_first, f610_second, f610_third, f650_first, f650_second, f650_third, f650_forth, f655_first, f700_first, f700_second, f700_third,  f710_first, f710_second, f710_third, tick)
					logger.info("Updated in db")
					sleep(1)							
					try:
						ws.delete_row(my_row_numb)
						logger.info("Deleted from spreadsheet")
						sleep(1)
						my_row_numb = my_row_numb-1
					except Exception as e:
						logger.warning(str(e))
						logger.info("Waiting for 50 seconds")
						sleep(50)
						try:
							ws = self.load_spreadsheet()
							ws.delete_row(my_row_numb)
							my_row_numb = my_row_numb-1

							
						except Exception as e:
							logger.warning(str(e))



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

		# self.file_cleaning()

		# self.get_ies_from_reports()
		# lst = self.read_ies_file()
		# self.insert_ies()

		self.finish_existing_records_and_delete_files("prod")#update with 942 and make items and delete SIPs form prod (project and rosetta folder)

		self.db_handler.delete_done_from_db()

		self.update_database_from_spreadsheetand_delete_row() 

		my_rec = RecordCreator(self.alma_key)
		my_rec.record_creating_routine()

		sip_routine() #only 

		##############################################
		harvest() #first time when episode enter db
		self.db_handler.update_the_last_issue()
		# ###############################################

		 		
def main():

	podcast = Podcast_pipeline("prod")
	podcast.podcast_routine()


if __name__ == "__main__":
	main()
