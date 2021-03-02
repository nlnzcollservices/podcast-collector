from alma_tools import AlmaTools
import csv

csv_path = r"Y:\ndha\pre-deposit_prod\LD_Proj\podcasts\assets\wrong_items_list.csv"
my_alma = AlmaTools("prod")
with open (csv_path,"r") as f:
	data = csv.reader(f)
	next(data, None)
	for el in data:
		my_alma.xml_response_data = None
		mms = el[-1]
		holding = el[-2]
		item = el[-3]
		title = el[0]
		print(title, holding, item, mms)
		my_alma.get_item(mms, holding, item)
		#print(my_alma.xml_response_data)
		my_alma.xml_response_data = my_alma.xml_response_data.replace("POL-103768", "POL-119744")
		#print(my_alma.xml_response_data)
		my_alma.update_item(mms, holding, item, my_alma.xml_response_data)
		print(my_alma.status_code)
		print(my_alma.xml_response_data)		
