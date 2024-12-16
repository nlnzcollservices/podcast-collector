import hashlib
import time
import json
import os
import sys
import dateparser
from podcast_dict import podcasts_dict, serials
from rosetta_sip_factory.sip_builder import build_sip_from_json
import shutil
from settings import log_folder, file_folder, sip_folder, rosetta_folder, rosetta_folder_for_serials, logging, ie_entity_type, ie_entity_type_serial, rosetta_sb_folder, report_folder
from podcasts_database_handler import DbHandler
sys.path.insert(0, r"Y:\ndha\pre-deposit_prod\LD_working\alma_tools")
from alma_tools import AlmaTools
logger = logging.getLogger(__name__)


def generate_md5(filepath):

	"""Taking fixity of audio file
	Parameters:
		filepath(str) - path to file to make a fixity
	Returns:
		hash_md5.hexdigest(str) - fixity
	"""

	hash_md5 = hashlib.md5()
	with open(filepath, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_md5.update(chunk)
	return hash_md5.hexdigest()


def generate_sips(podcast_name, ar_policy, serial_mms,  mis_mms,  episode_title, filepath ):

	"""Generates SIPs

	Parameters:
		podcast_name(str) - podcast_name
		ar_policy(str) - access right policy code. Set 100 in settings. (100 for open source, 200 for limited access, 400 for "dark archive")
		serial_mms(str) - Alma mms id of serial_record
		mis_mms(str) -Alma mms id for episode record
		episode_title(str) - episode title
		filepath(str) - filepath
	Returns:
		output_dir(str) - path to sips that belong to one podcast name appear as serial mms id in project folder
		filename(str) - filename
	"""

	filename= os.path.basename(filepath)
	ie_dmd_dict = [{'dc:title': episode_title}]
	general_ie_chars = [{'IEEntityType': ie_entity_type,"UserDefinedA":"podcasts"}]
	object_identifier=[{'objectIdentifierType': 'ALMAMMS','objectIdentifierValue': mis_mms}]
	access_rights_policy = [{'policyId': ar_policy}]
	sip_title = str(serial_mms)
	output_dir = os.path.join(sip_folder, sip_title)
	#simple_file_name = os.path.basename(full_filename)
	file_original_path = f'{mis_mms}/{filename}'
	my_json = {}
	my_json['physical_path'] = filepath
	my_json["fileOriginalName"]= filename
	my_json["fileOriginalPath"] = file_original_path
	my_json["MD5"] = generate_md5(filepath)
	my_json["fileSizeBytes"] = str(os.path.getsize(filepath))
	my_json["fileCreationDate"] = time.strftime("%Y-%m-%dT%H:%M:%S",time.localtime(os.path.getctime(filepath)))
	my_json["fileModificationDate"] = time.strftime("%Y-%m-%dT%H:%M:%S",time.localtime(os.path.getmtime(filepath)))
	my_json["label"] = podcast_name + ": " + episode_title
	pres_master_json = json.dumps(my_json)
	json_object = json.loads(pres_master_json )
	json_object['fileOriginalPath'] = json_object['fileOriginalPath']
	json_object['MD5'] = json_object['MD5']
	pres_master_json = json.dumps([json_object])
	build_sip_from_json(
				ie_dmd_dict=ie_dmd_dict,
				pres_master_json=pres_master_json,
				generalIECharacteristics=general_ie_chars,
				objectIdentifier=object_identifier,
				accessRightsPolicy=access_rights_policy,
				digital_original=True,
				sip_title=sip_title,
				input_dir = file_folder,
				output_dir=output_dir,
				mets_filename=mis_mms,
				structmap_type="PHYSICAL",
				encoding = "utf-8"
	)
	logger.info (f"{mis_mms} - Done")
	return output_dir, filename

def generate_sips_for_serials (podcast_name, ar_policy, serial_mms,  episode_title, filepath, met_filename ):

	"""Generates SIPs fro serial records

	Parameters:
		podcast_name(str) - podcast_name
		ar_policy(str) - access right policy code. Set 100 in settings. (100 for open source, 200 for limited access, 400 for "dark archive")
		serial_mms(str) - Alma mms id of serial_record
		episode_title(str) - episode title
		filepath(str) - filepath
	Returns:
		output_dir(str) - path to sips that belong to one podcast name appear as serial mms id in project folder
		filename(str) - filename
	"""
	year = ""
	month = ""
	day = ""
	title_for_label = str(episode_title)
	title_for_dc_title = str(episode_title)
	if podcast_name in ["Kelli from the Tron"]:
		my_date = episode_title.split(" ")[-1]
		title_for_dc_title = episode_title.split("-")[0].rstrip(" ")
		title_for_label = "_".join(episode_title.split("-")[-3:]).lstrip(" ")
		day = dateparser.parse(my_date).strftime("%d")
		month = dateparser.parse(my_date).strftime("%m")
		year = dateparser.parse(my_date).strftime("%Y")
	filename= os.path.basename(filepath)
	ie_dmd_dict = [{'dc:title': title_for_dc_title,"dc:date":year,"dcterms:available":month, "dc:coverage":day }]
	general_ie_chars = [{'IEEntityType': ie_entity_type_serial}]#HERE Userdefind
	object_identifier=[{'objectIdentifierType': 'ALMAMMS','objectIdentifierValue': serial_mms}]
	access_rights_policy = [{'policyId': ar_policy}]
	sip_title = title_for_dc_title + str(serial_mms)
	output_dir = os.path.join(sip_folder, title_for_dc_title)
	#simple_file_name = os.path.basename(full_filename)
	file_original_path = f'{filename}'
	my_json = {}
	my_json['physical_path'] = filepath
	my_json["fileOriginalName"]= filename
	my_json["fileOriginalPath"] = file_original_path
	my_json["MD5"] = generate_md5(filepath)
	my_json["fileSizeBytes"] = str(os.path.getsize(filepath))
	my_json["fileCreationDate"] = time.strftime("%Y-%m-%dT%H:%M:%S",time.localtime(os.path.getctime(filepath)))
	my_json["fileModificationDate"] = time.strftime("%Y-%m-%dT%H:%M:%S",time.localtime(os.path.getmtime(filepath)))
	my_json["label"] = podcast_name + ": " + title_for_label
	pres_master_json = json.dumps(my_json)
	json_object = json.loads(pres_master_json )
	json_object['fileOriginalPath'] = json_object['fileOriginalPath']
	json_object['MD5'] = json_object['MD5']
	pres_master_json = json.dumps([json_object])
	build_sip_from_json(
					ie_dmd_dict=ie_dmd_dict,
					pres_master_json=pres_master_json,
					generalIECharacteristics=general_ie_chars,
					objectIdentifier=object_identifier,
					accessRightsPolicy=access_rights_policy,
					digital_original=True,
					sip_title=sip_title,
					input_dir = file_folder,
					output_dir=output_dir,
					mets_filename=met_filename.split(".")[0],
					structmap_type="PHYSICAL",
					encoding = "utf-8",
					exclude_file_char = ['fileOriginalPath','fileSizeBytes', 'fileModificationDate','fileCreationDate']
	)
	logger.info (f"{episode_title} - Done")
	return output_dir, filename

def sip_checker(output_dir,   mis_mms, filename, filesize, podcast_name):

	"""Checks if met.xml files (mis_mms_id + .xml) is empty, or filesize is 0 byte, or filesize is not equal to original fileSizeBytes
	Parameters:
		output_dir(str) - path to sips that belong to one podcast name appear as serial mms id in project folder
		mis_mms (str) - Alma mms id of episode record
		filesize (str) - original filesize
		podcast_name (str) - name of podcast
	Returns:
		flag(bool) - True if no error found.  False if size of file is wrong or audio file or met file are empty.
	"""
	flag = True
	if os.path.getsize(os.path.join(output_dir, "content", mis_mms +".xml")) == 0:
		logger.info("Attention - empty met! {} {} {}".format(podcast_name, mis_mms, filename))
		flag = False

	if os.path.getsize(os.path.join(output_dir,  "content", "streams", mis_mms, filename )) == 0:
		logger.info("Attention - empty file! {} {} {} {}".format(podcast_name, mis_mms, filename, filesize))
		flag = False
	if filesize:
		if os.path.getsize(os.path.join(output_dir,  "content", "streams", mis_mms, filename))!=int(filesize):
			logger.info("Attention - wrong filesize!{} {} {} {}".format(podcast_name, mis_mms, filename, filesize))
			flag = False
				
	return flag

def sip_checker_serial(output_dir, met_filename,  filename, filesize, podcast_name):

	"""Checks if met.xml files (mis_mms_id + .xml) is empty, or filesize is 0 byte, or filesize is not equal to original fileSizeBytes
	Parameters:
		output_dir(str) - path to sips that belong to one podcast name appear as serial mms id in project folder
		mis_mms (str) - Alma mms id of episode record
		filesize (str) - original filesize
		podcast_name (str) - name of podcast
	Returns:
		flag(bool) - True if no error found.  False if size of file is wrong or audio file or met file are empty.
	"""
	print("Test")

	flag = True
	if os.path.getsize(os.path.join(output_dir, "content", met_filename)) == 0:
		logger.info("Attention - empty met! {} {} {}".format(podcast_name, met_filename, filename))
		flag = False

	if os.path.getsize(os.path.join(output_dir,  "content", "streams",  filename )) == 0:
		logger.info("Attention - empty file! {} {} {}".format(podcast_name, filename, filesize))
		flag = False
	if filesize:
		if os.path.getsize(os.path.join(output_dir,  "content", "streams", filename))!=int(filesize):
			logger.info("Attention - wrong filesize!{} {} {}".format(podcast_name, filename, filesize))
			flag = False
				
	return flag
def copy_sip(output_dir, destination, mis_mms, filename):

	"""
	Copying entire sip directory form project folder to destination
	Parameters:
		output_dir(str) - folders which contains sips in project sip folder
		destination(str) - rosetta production or sb folder
		filename(str) - name of file
	"""
	content_folder = os.path.join(destination,"content")
	print(content_folder)
	if not os.path.isdir(destination):
		os.makedirs(os.path.join(destination, "content", "streams"))
	elif not os.path.isdir(content_folder):
		os.makedirs(os.path.join(destination, "content", "streams"))
	shutil.copyfile(os.path.join(output_dir, "content", "dc.xml"), os.path.join(destination, "content", "dc.xml"))
	shutil.copyfile(os.path.join(output_dir, "content", mis_mms+".xml"), os.path.join(destination, "content", mis_mms+".xml"))
	if not os.path.isdir(os.path.join(destination, "content", "streams", mis_mms)):
		os.makedirs(os.path.join(destination, "content", "streams", mis_mms))
	shutil.copyfile(os.path.join(output_dir, "content", "streams", mis_mms, filename ),os.path.join(destination, "content", "streams", mis_mms, filename) )
	# After the SIP has been copied, create a ready-for-ingestion file so the dashboard will pick it up"
	with open(os.path.join(destination, "ready-for-ingestion-FOLDER-COMPLETED"), 'w') as f:
		f.write("")


def copy_sip_serial(output_dir, destination, filename, met_filename):

	"""
	Copying entire sip directory form project folder to destination
	Parameters:
		output_dir(str) - folders which contains sips in project sip folder
		destination(str) - rosetta production or sb folder
		filename(str) - name of file
	"""
	
	content_folder = os.path.join(destination,"content")
	print(content_folder)
	if not os.path.isdir(destination):
		os.makedirs(os.path.join(destination, "content", "streams"))
	elif not os.path.isdir(content_folder):
		os.makedirs(os.path.join(destination, "content", "streams"))
	shutil.copyfile(os.path.join(output_dir, "content", "dc.xml"), os.path.join(destination, "content", "dc.xml"))
	shutil.copyfile(os.path.join(output_dir, "content", met_filename), os.path.join(destination, "content", met_filename))
	shutil.copyfile(os.path.join(output_dir, "content", "streams", filename ),os.path.join(destination, "content", "streams", filename) )
	# After the SIP has been copied, create a ready-for-ingestion file so the dashboard will pick it up"
	with open(os.path.join(destination, "ready-for-ingestion-FOLDER-COMPLETED"), 'w') as f:
		f.write("")



def sip_routine(podcast_list=[], copy_to_rosetta_prod_folder = True, copy_to_sb_folder = False, update_sip_in_db = True):

	"""
	Manages the process of creating SIPs if record already created in Alma and has mms id. Updates db with sip equals True. Runs sip_checker. Copying SIPs to sb or production folder depending on Parameters.
	Parameters:
		podcast_list (list) - contains name of podcasts to create SIPs for. If set [] goes across all the podcasts.
		copy_to_rosetta_prod_folder - True by default and the SIP will be copied to production folder, otherwise the parameter should set False
		copy_to_sb_folder - False by default and the SIP will not be copied to sandbox folder, otherwise the parameter should be set True
		update_sip_in_db - True by default and db will be updated with sip = True, otherwise should be set False

	"""

	my_db = DbHandler()
	to_do_flag = False
	sip_count = 0
	file_count = 0
	my_dict=my_db.db_reader(["podcast_name", "serial_mms", "access_policy", "mis_mms","episode_title","publish_link_to_record","tick","filepath","filesize","sip"], podcast_list, True)
	logger.info("Making SIPs")
	for episode in my_dict:
		#print(episode)
		if "mis_mms" in episode.keys():# or (not "mis_mms" in episode.keys() and "serial" in podcast_dict[my_dict["podcast_name"].keys()):
			ar_policy = episode["access_policy"]
			podcast_name =  episode["podcast_name"]
			serial_mms = episode["serial_mms"]
			mis_mms = episode["mis_mms"]
			logger.debug(mis_mms)
			episode_title = episode["episode_title"]
			publish_link_to_record = episode["publish_link_to_record"]
			tick = episode["tick"]
			sip = episode["sip"]
			filepath = episode["filepath"]
			logger.debug(episode["podcast_name"])
			logger.debug(episode["episode_title"])
			logger.debug(episode["filepath"])
			logger.debug("!!!")

			filesize = episode["filesize"]
			if tick and mis_mms and filepath and not sip:
				logger.info(mis_mms)
				file_count +=1
				output_dir, filename = generate_sips(podcast_name, ar_policy, serial_mms,  mis_mms,  episode_title, filepath)
				logger.info("SIP created in " + output_dir)
				my_check = sip_checker(output_dir, mis_mms, filename, filesize, podcast_name)
				if my_check:
					if update_sip_in_db:
						my_db.db_update_sip(episode_title, podcast_name)
					if copy_to_rosetta_prod_folder:
						destination = os.path.join(rosetta_folder, serial_mms )
					if copy_to_sb_folder:
						destination = os.path.join(rosetta_sb_folder, serial_mms )
					if serial_mms in serials:
						destination = os.path.join(rosetta_folder_for_serials, serial_mms)
					if copy_to_rosetta_prod_folder or copy_to_sb_folder:
						try:
							copy_sip(output_dir, destination, mis_mms, filename)
							sip_count+=1
						except Exception as e:
							logger.error(str(e))
							try:
								copy_sip(output_dir, destination, mis_mms, filename)
								sip_count+=1
							except Exception as e:
								logger.error(str(e))
								quit()
						logger.info("Copied to {}".format(destination))
						with open(os.path.join(report_folder, "sips.txt"), "a") as f:
							f.write(os.path.join(destination, "content", mis_mms))
							f.write("\n")

				else:
					logger.error("Something wrong with file {} {} {}".format(podcast_name, filename, mis_mms))
					quit()

			elif tick and not mis_mms and filepath and not sip and serial_mms in serials:
				file_count +=1
				met_filename = episode_title.replace(" ","_")+".xml"
				output_dir, filename = generate_sips_for_serials(podcast_name, ar_policy, serial_mms, episode_title, filepath, met_filename)
				logger.info("SIP created in " + output_dir)
				my_check = sip_checker_serial(output_dir, met_filename, filename, filesize, podcast_name)

				if my_check:
					if update_sip_in_db:
						my_db.db_update_sip(episode_title, podcast_name)
					if copy_to_rosetta_prod_folder:
						destination = os.path.join(rosetta_folder_for_serials, episode_title.split('-')[0].rstrip(" ") )
					if copy_to_sb_folder:
						destination = os.path.join(rosetta_sb_folder, episode_title.split('-')[0].rstrip(" ") )
					if copy_to_rosetta_prod_folder or copy_to_sb_folder:
						print("TEST!")
						try:
							copy_sip_serial(output_dir, destination, filename, met_filename)
							sip_count+=1
						except Exception as e:
							logger.error(str(e))
							try:
								copy_sip_serial(output_dir, destination, filename, met_filename)
								sip_count+=1
							except Exception as e:
								logger.error(str(e))
								quit()
						logger.info("Copied to {}".format(destination))
						my_db.db_update_sip(episode_title, podcast_name)
						with open(os.path.join(report_folder, "sips.txt"), "a") as f:
							f.write("{}|{}".format(destination, episode_title))
							f.write("\n")



				else:
					logger.error("Something wrong with file {} {} {}".format(podcast_name, filename, mis_mms))
					quit()
			if not filepath:
				logger.error("No filepath for {} {} {}".format(podcast_name, filename, mis_mms))
	

	if sip_count == file_count:
		logger.info("The numbers of files {} and sips {} match".format(file_count, sip_count))

	else:
		logger.error("The numbers of files {file_count} and sips {sip_count} does not match!!!".format(file_count, sip_count))
		quit()



def main():

	"""This runs the sip_routine"""
	#Example
	#[] - send empty list to run over all the podcast names or fill it with podcast names to process.
	#copy_to_rosetta_prod_folder = False - for not copying there. By default it is True	
	#copy_to_sb = True - for copying ready SIPs to sb folder. It is False by default
	#update in db = set False not to update
	#The following command make sips for all the podcast names, copy them to sb folder, does not update db with sip = True)
	sip_routine([],False, True, False)


if __name__ == '__main__':
	main()