import sys
import os
import re
import urllib3
sys.path.insert(0, r"Y:\ndha\pre-deposit_prod\LD_working\alma_tools")
from alma_tools import AlmaTools
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



sip_folder = r"Y:\ndha\pre-deposit_prod\server_side_deposits\prod\ld_scheduled\oneoff_audio\9918878773402836\content"
at = AlmaTools("prod")

for el in os.listdir(sip_folder):
	my_mms = el.split(".")[0]
	if my_mms.isdigit():
		print(my_mms)

		#check mms exists

		#at.get_bib(my_mms)
			# if at.status_code in [200,204]:
		# 	print("Ok")
		# else:
		# 	print("!!!!!!!!!!!!!!!CHECK")
		

		#Check repres less ore more then one

		at.get_representations(my_mms)
		rec_count = re.findall(r'record_count="(.*?)">', at.xml_response_data)[0]
		if int(rec_count) !=1:
			print("!!!!!!!!!!!!!!!!!!!")
			print(rec_count)
			print(at.xml_response_data)

