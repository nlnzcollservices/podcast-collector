	try:
	from settings import logging, template_folder,start_xml, end_xml, report_folder
except:
	from settings_prod import logging, template_folder,start_xml, end_xml, report_folder

import os
import io
from alma_tools import AlmaTools
from pymarc import parse_xml_to_array#,record_to_xml, Field 


#mms_file = os.path.join(report_folder, "mms.txt")
mms_file = None

def main(title_list = None, mms_list = None):

	"""Deletes bibliographic records by mms from lst or from mms.txt file if the title in title_list.With abscence of mms list takes mms ids from mms.txt file. With abscence 
	Arguments:
		title_list(list) - contains titles to delete. None by default.
		mms_list(list) - 
	Returns:
		None
	"""

	my_alma = AlmaTools("prod")
	if not mms_list:
		mms_list =[]
		with open mms_file as f:
		 	data = f.read()
		for el  in data.split("\n")[:-1]:
			mms_list.append(el)
	for el in mms_list:
		my_alma.get_bib(el)
		#print(my_alma.xml_response_data)
		if my_alma.status_code == 200:
			record = parse_xml_to_array(io.StringIO(my_alma.xml_response_data))[0]
			title = record["245"]["a"]
			print(title)
			title = title.rstrip(".")#.rstrip("!")
			if title in title_list or title in title_list2 or title in title_list3:
				my_alma.delete_bib(record["001"].data)
				print(my_alma.status_code)
				print(my_alma.xml_response_data)
				print(el)


if __name__ == '__main__':
	main()

