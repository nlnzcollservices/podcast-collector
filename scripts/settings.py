import os
import sys
import configparser
from datetime import datetime as dt
from oauth2client import file
import json
import logging
import logging.config
import httplib2


#********************SETTINGS FILE FOR ALL PODCAST SCRTIPTS****************#

#######################Setting path for all the parts#######################

script_folder = os.getcwd()
working_folder = "\\".join(script_folder.split("\\")[:-1])
file_folder = os.path.join(working_folder, "files")
logs_folder = os.path.join(working_folder, "log")
assets_folder = os.path.join(working_folder,"assets")
template_folder = os.path.join(assets_folder, "templates")
report_folder= os.path.join(assets_folder, "reports")
log_folder = os.path.join(logs_folder, "log")
database_folder = os.path.join(working_folder, "database")
database_fullname = os.path.join(database_folder, "podcasts.db")
sip_folder = os.path.join(working_folder, "SIP")
rosetta_folder = r"Y:\NDHA\pre-deposit_prod\server_side_deposits\prod\ld_scheduled\oneoff_audio"
rosetta_sb_folder = r"Y:\NDHA\pre-deposit_prod\server_side_deposits\UAT\podcasts"
archived_folder = os.path.join(working_folder, "archived")
database_archived_folder = os.path.join(working_folder, "archived","db_copy")
ndha_report_folder = os.path.join(report_folder, "NDHA_reports")
ndha_used_report_folder = os.path.join(report_folder, "NDHA_used_reports")
done_ies = os.path.join(report_folder,"done_report_ies.txt")
deleted_items_holdings = os.path.join(report_folder, "deleted_iems_holdings.txt")
########################Setting folder for git scripts######################

# *-mainly used for Amy's downloader but might be used for other modules downloaded from git storage
git_folder = r"C:\Users\granthrh\Documents\NDHA\NDHA\project\file-downloader"
sys.path.insert(0, git_folder)

########################SETTING FOLDER FOR CREDENTIAL FILES#################

# *-used for proxies, google credentials, alma APIs and DNZ APIs
secrets_and_credentials_fold = r'H:\Secrets'
sys.path.insert(0, secrets_and_credentials_fold)
secret_file = os.path.join(secrets_and_credentials_fold, "shopping") 
config = configparser.ConfigParser()
config.read(secret_file)

#######################Setting google sreadsheet credentials#################

#* - google spreadsheet code could be replaced on another one
podcast_sprsh = config.get("configuration", "google_spreadsheet_key")

#* - getting google credentials from client_secrect.json file
client_secrets_file = os.path.join(secrets_and_credentials_fold, "client_secrets.json")
store = file.Storage(client_secrets_file )
creds = store.get()
# * - this part could be removed after setting new tokens
if creds.access_token_expired:
    creds.refresh(httplib2.Http())

####################Getting API keys from secret file##########################

pr_key = config.get( "configuration", "production") 
sb_key= config.get("configuration", "sandbox")	

######################Only need for DNZ ##############################################
#* - optional only requered for getting information about preserved sips and might not be used
#credential_file = os.path.join(secrets_and_credentials_fold, "credentials")

##########################Getting proxies##############################################
#* - optional might not be used and removed from requests

# proxy_file = os.path.join(secrets_and_credentials_fold, "proxies.json")
# with open(proxy_file, "r") as f_proxy:
# 	proxies = json.load(f_proxy)

############################Logging#####################################################
	
#Logging levels:
# DEBUG: Detailed information, for diagnosing problems. Value=10.
# INFO: Confirm things are working as expected. Value=20.
# WARNING: Something unexpected happened, or indicative of some problem. But the software is still working as expected. Value=30.
# ERROR: More serious problem, the software is not able to perform some function. Value=40
# CRITICAL: A serious error, the program itself may be unable to continue running. Value=50


logging.basicConfig(level=logging.INFO,  datefmt='%Y-%m-%d %H:%M:%S', format = "%(name)15s (%(levelname)s) : %(message)s[%(asctime)s]")
	
#only messages from logging.<your level> and higher levels will get logged.

##################################Record XML tags######################################

## Strings to wrap XML
start_xml = r'<?xml version="1.0" encoding="UTF-8"?><bib><record_format>marc21</record_format><suppress_from_publishing>false</suppress_from_publishing><suppress_from_external_search>false</suppress_from_external_search><sync_with_oclc>BIBS</sync_with_oclc>'
end_xml = '</bib>'

###############################SIP settings###############################################
ie_entity_type = 'AudioIE'
##################################e-mail settings########################################
my_email_box = "Rhonda.grantham@dia.govt.nz"
report_part_name = "45. Weekly Published"
#####################################SET UP Folders#######################################
## Run the current script to create full folder structure





def main():
	for folder in [file_folder , script_folder, assets_folder, template_folder, logs_folder, database_folder, report_folder,  log_folder, database_fullname, sip_folder,archived_folder, database_archived_folder, ndha_report_folder, ndha_used_report_folder]:
		print(folder)
		if not os.path.exists(folder):
			os.mkdir(folder)


if __name__ == '__main__':
	main()