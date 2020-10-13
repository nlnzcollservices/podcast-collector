import hashlib
import time
import json
import os
from rosetta_sip_factory.sip_builder import build_sip_from_json
import shutil
from settings import log_folder, file_folder, sip_folder, rosetta_folder, logging, ie_entity_type, rosetta_sb_folder, report_folder
from database_handler import DbHandler



def generate_md5(filepath):

		hash_md5 = hashlib.md5()
		with open(filepath, "rb") as f:
			for chunk in iter(lambda: f.read(4096), b""):
				hash_md5.update(chunk)
		return hash_md5.hexdigest()


def generate_sips(podcast_name, ar_policy, serial_mms,  mis_mms,  episode_title,filepath ):

		filename = os.path.basename(filepath)
		ie_dmd_dict = [{'dc:title': episode_title}]
		general_ie_chars = [{'IEEntityType': ie_entity_type}]
		object_identifier=[{'objectIdentifierType': 'ALMAMMS','objectIdentifierValue': mis_mms}]
		access_rights_policy = [{'policyId': ar_policy}]
		sip_title = serial_mms
		output_dir = os.path.join(sip_folder, sip_title)
		#simple_file_name = os.path.basename(full_filename)
		file_original_path = f'{mis_mms}/{filename}'
		my_json = {}
		my_json['physical_path'] = filepath
		my_json["fileOriginalName"]= filename
		my_json["fileOriginalPath"] = file_original_path,
		my_json["MD5"] = generate_md5(filepath),
		my_json["fileSizeBytes"] = str(os.path.getsize(filepath))
		my_json["fileCreationDate"] = time.strftime("%Y-%m-%dT%H:%M:%S",time.localtime(os.path.getctime(filepath)))
		my_json["fileModificationDate"] = time.strftime("%Y-%m-%dT%H:%M:%S",time.localtime(os.path.getmtime(filepath)))
		my_json["label"] = episode_title
		pres_master_json = json.dumps(my_json)
		json_object = json.loads(pres_master_json )
		json_object['fileOriginalPath'] = json_object['fileOriginalPath'][0]
		json_object['MD5'] = json_object['MD5'][0]
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
		logging.info (f"{mis_mms} - Done")
		return output_dir, filename

def sip_checker(output_dir,   mis_mms, filename, filesize, podcast_name):

	if os.path.getsize(os.path.join(output_dir, "content", mis_mms +".xml")) == 0:
		logging.info("Attention - empty met! {} {} {}".format(podcast_name, mis_mms, filename))
		flag = False
	else:
		flag = True
	if os.path.getsize(os.path.join(output_dir,  "content", "streams", mis_mms, filename )) == 0:
		logging.info("Attention - empty file! {} {} {} {}".format(podcast_name, mis_mms, filename, filesize))
		flag = False
	else:
		flag = True
	if filesize:
		if os.path.getsize(os.path.join(output_dir,  "content", "streams", mis_mms, filename))!=int(filesize):
			logging.info("Attention - wrong filesize!{} {} {} {}".format(podcast_name, mis_mms, filename, filesize))
			flag = False
		else:
			flag = True						
	return flag
	
def copy_sip(output_dir, destination, mis_mms, filename):

	if not os.path.isdir(destination):
		os.makedirs(os.path.join(destination, "content", "streams"))
	shutil.copyfile(os.path.join(output_dir, "content", mis_mms+".xml"), os.path.join(destination, "content", "dc.xml"))
	shutil.copyfile(os.path.join(output_dir, "content", mis_mms+".xml"), os.path.join(destination, "content", mis_mms+".xml"))
	if not os.path.isdir(os.path.join(destination, "content", "streams", mis_mms)):
		os.makedirs(os.path.join(destination, "content", "streams", mis_mms))
	shutil.copyfile(os.path.join(output_dir, "content", "streams", mis_mms, filename ),os.path.join(destination, "content", "streams", mis_mms, filename) )



def sip_routine(podcast_list=[], copy_to_rosetta_prod_folder = True, copy_to_sb_folder = False, update_sip_in_db = True):

		my_db = DbHandler()
		to_do_flag = False
		sip_count = 0
		file_count = 0
		my_dict=my_db.db_reader(["podcast_name", "serial_mms", "access_policy", "mis_mms","episode_title","publish_link_to_record","tick","filepath","filesize","sip"], podcast_list)
		for episode in my_dict:
			if "mis_mms" in episode.keys():
				ar_policy = episode["access_policy"]
				podcast_name =  episode["podcast_name"]
				serial_mms = episode["serial_mms"]
				mis_mms = episode["mis_mms"]
				episode_title = episode["episode_title"]
				publish_link_to_record = episode["publish_link_to_record"]
				tick = episode["tick"]
				sip = episode["sip"]
				filepath = episode["filepath"]
				filesize = episode["filesize"]
				if tick and mis_mms and filepath and not sip:
					file_count +=1
					output_dir,filename = generate_sips(podcast_name, ar_policy, serial_mms,  mis_mms,  episode_title, filepath)
					my_check = sip_checker(output_dir, mis_mms, filename, filesize, podcast_name)
					if my_check:
						if update_sip_in_db:
							my_db.db_update_sip(episode_title)
						if copy_to_rosetta_prod_folder:
							destination = os.path.join(rosetta_folder, serial_mms )
						if copy_to_sb_folder:
							destination = os.path.join(rosetta_sb_folder, serial_mms )
						if copy_to_rosetta_prod_folder or copy_to_sb_folder:
							try:
								copy_sip(output_dir, destination, mis_mms, filename)
								sip_count+=1
							except Exception as e:
								logging.debug(str(e))
								try:
									copy_sip(output_dir, destination, mis_mms, filename)
									sip_count+=1
								except Exception as e:
									logging.debug(str(e))
									quit()
							logging.info("Copied to {}".format(destination))
							with open(os.path.join(report_folder, "sips.txt"), "a") as f:
								f.write(os.path.join(destination, "content", mis_mms))
								f.write("\n")

					else:
						quit()
				if not filepath:
					logging.info(f"No filepath for {podcast_name} {episode_title} {mis_mms}")
					quit()
		if sip_count == file_count:
			logging.info("The numbers of files {} and sips {} match".format(file_count, sip_count))

		else:
			logging.info("The numbers of files {file_count} and sips {sip_count} does not match!!!".format(file_count, sip_count))
			quit()



def main():
	"""This runs the sip_routine"""
	#Example
	#[] - send empty list to run over all the podcast names or feel it with podcast names to process.
	#copy_to_rosetta_prod_folder = False - for not copuing there. By defaule it is True	
	#copy_to_sb = True - for copying ready SIPs to sb folder. It is False by default
	#update in db = set False not to update
	#The following command make sips for all the podcast names, copy them to sb folder, does not update db with sip = True)
	sip_routine([],False, True, False)

	pass

if __name__ == '__main__':
	main()