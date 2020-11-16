import os
import hashlib
import gspread
from datetime import datetime as dt
from database_handler import DbHandler
from alma_tools import AlmaTools

try:
	from settings import  logging, creds, podcast_sprsh, database_archived_folder, database_fullname, file_folder, report_folder, sip_folder, rosetta_folder, client_secrets_file, archived_folder, ndha_report_folder, ndha_used_report_folder, my_email_box, report_part_name, done_ies
except:
	from settings_prod import  logging, creds, podcast_sprsh, database_archived_folder, database_fullname, file_folder, report_folder, sip_folder, rosetta_folder, client_secrets_file, archived_folder, ndha_report_folder, ndha_used_report_folder, my_email_box, report_part_name, done_ies
from downloader_light_modified import DownloadResource as Downloader
import subprocess
from nltk.corpus import words 



c = gspread.authorize(creds)
gs = c.open_by_key(podcast_sprsh)
#change if the name or id of the worksheet is different
ws = gs.get_worksheet(0)


def jhove_check(filepath):

		command = [r'jhove',filepath,'-t', 'text'] # the shell command
		process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		output, error = process.communicate()
		output = str(output).split(r"\r\n")[1:-1]
		for el in output:
			if 'Status' in el:
				if "Well-Formed and valid" in el:
					return True
		return False

def check_for_meaning(my_filename):

		"""Checks filename for possible meaningfull words
		Parameters:
			my_filename (str) - filename to check
		Returns:
			word_meaning_flag(bool) - set True if meaningfull word found
		"""
		word_meaning_flag = False
		lst1  = []
		lst2 = []
		lst3=[]
		logging.info(f"Checking for meaning {my_filename}")
		if "." in my_filename:
			my_filename = my_filename.split(".")[0]
		if "-" in my_filename:
			lst1 = my_filename.split("-")
		if "_" in my_filename:
			lst2=my_filename.split("_")
		if '+' in my_filename:
			lst3 = my.split('+')
		lst = lst1+lst2+lst3
		for el in lst:
			if el.lower() in words.words():
				word_meaning_flag = True
		return word_meaning_flag

def get_metadata_from_row(rows_list):

	"""
	This function aimed to read manually entered to spreadsheet information and insert it to db to make it available for next apperations. Used for podcasts with short rss feed. (eg. Business is boring)
	for missing episodes (in this case only download link should be sprcified in google speadsheet) or for episodes which were downloaded through browser or given directly
	by providers (in this case path to file should be given too - the very last column).
	Arguments:
		row_list(list) - list of integers equals google spreadsheet row numbers

	Returns:
		none
	"""

	logging.info("Updating spreadsheet")
	start_point = 0
	end_point = ws.row_count-1
	my_row_numb = 1
	filepath = None
	episode_season = None
	episode_number = None
	md5 = None
	md5_original = None
	filesize = None
	size_original = None
	file_type  =  None
	
	for ind  in range(start_point, end_point):
		my_row_numb = ind+2
		flag_for_epis_table = False
		
		if my_row_numb in rows_list:
			my_row = ws.row_values(my_row_numb)
			logging.info(my_row_numb)
			#not filepath entered
			if len(my_row)<= 28:
				podcast_name = my_row[0]
				episode_title = my_row[3].lstrip(" ").rstrip(" ")
				description = my_row[4]
				episode_link = my_row[5]
				episode_date = my_row[6]
				tags = my_row[7]
				episode_download_link = my_row[8]
			#filepath in the spreadsheet which means that file already downloaded
			if len(my_row)>=33:	
				episode_number = my_row[30]
				episode_season = my_row[31]
				filepath = my_row[32]
				print(filepath)
			if not filepath:
				f_path = os.path.join(file_folder, podcast_name.strip('’'))
				downloader = Downloader(episode_download_link, f_path, collect_html=False, proxies=None)
				logging.info(downloader.message)
				if downloader.size_original == 0:
					logging.info("Ther is empty file on {} in {} of {}. Please contact publisher".format(episode_download_link, episode_title, podcast_name))
					spreadsheet_message = "!!!D Not Tick. Empty file. Ask piblisher!!!"
				print(downloader.filepath)
				if not downloader.download_status or not jhove_check(downloader.filepath) or (downloader.filesize == 0 and downloader.size_original != 0):
					downloader = Downloader(episode_download_link, f_path, collect_html=False, proxies=None)
					if not downloader.download_status:
						downloader.message
					if not jhove_check(downloader.filepath):
						logging.debug("File is not well-formed")
						quit()
				if downloader.filename_from_headers or downloader.filename_from_url:
					if downloader.filename_from_headers or downloader.filename_from_url:
						if downloader.filename_from_headers and downloader.filename_from_headers != "media.mp3":									
							if check_for_meaning(downloader.filename_from_headers):
								downloader.change_filename(rename_from_headers = True)
								logging.info(f"filename from headers {downloader.filename_from_headers}")
						elif downloader.filename_from_url and downloader.filename_from_url != "media.mp3":
							logging.info(f"file name from url {downloader.filename_from_url}")
							if check_for_meaning(downloader.filename_from_url):
								downloader.change_filename(rename_from_url = True)
						if downloader.exists:
							downloader.filepath = downloader.new_filepath
							downloader.filename = downloader.new_filename
				filepath = downloader.filepath
				md5 = downloader.md5
				md5_original = downloader.md5_original
				filesize = downloader.filesize
				size_original = downloader.size_original
				file_type  =  downloader.filetype_extension
			elif filepath:
				hash_md5 = hashlib.md5()
				with open(filepath, "rb") as f:
					for chunk in iter(lambda: f.read(4096), b""):
						hash_md5.update(chunk)
						md5 = hash_md5.hexdigest()
				filesize = os.path.getsize(filepath)
				filetype_extension = filepath.split(".")[-1]
			my_db = DbHandler()
			episode_dict = my_db.db_reader(["episode_title","episode_id"],[podcast_name],True)
			#Checks if the episode already in database
			for epsd in episode_dict:
					if not epsd == {}:
						if epsd["episode_title"] == episode_title:
							logging.info(f"the episode {episode_title} is in db")
							flag_for_epis_table = True
							if flag_for_epis_table:
								episode = epsd["episode_id"]

			if not flag_for_epis_table:
				podcast_id = my_db.get_podcast_id(podcast_name)
				episode_data = {"podcast": podcast_id,"episode_title":episode_title, "description":description, "date_harvested":str(dt.now().strftime( '%Y-%m-%d')), "date":episode_date, "harvest_link": episode_download_link, "episode_link":episode_link, "epis_numb" : episode_number, "epis_seas" : episode_season}
				my_db.table_creator("Episode", episode_data)
				episode = my_db.my_id.id
			file_data = {"episode" : episode, "filepath" : filepath, "md5sum" : md5, "md5_from_file" : md5_original, "filesize" : filesize, "size_original" : size_original, "file_type" : file_type}
			my_db.table_creator("File", file_data)
						

		 		
def main():

	get_metadata_from_row([651])

if __name__ == "__main__":
	main()
