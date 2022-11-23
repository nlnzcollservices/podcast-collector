from alma_tools import AlmaTools
import re
import io
from pymarc import parse_xml_to_array,record_to_xml, Field 

my_api = AlmaTools("prod")
file_name = "podcasts_set2.txt"


def get_records_from_set(set_id):

	my_api.get_set_members(set_id,{"limit":"100"})
	print(my_api.xml_response_data)
	total_count = re.findall(r'<members total_record_count="(.*?)">',my_api.xml_response_data)[0]
	for i in range((int(total_count)//100)+2):
		if i >18:
			my_api.get_set_members(set_id,{"limit":"100","offset":99*i})
			mms_ids = re.findall(r"<id>(.*?)</id>",my_api.xml_response_data)
			for mms in mms_ids:
				try:
					my_api.get_bib(mms)
				except:
					my_api.get_bib(mms)
				print(my_api.xml_response_data)
				my_data = "".join(my_api.xml_response_data.split("\n"))
				if "Record automatically derived from RSS feed" in my_api.xml_response_data and not "The Spinoff presents SUPERPOD" in my_api.xml_response_data:
					with open(file_name,"a", encoding = "UTF-8") as f:
						f.write(my_data)
						f.write("\n")


def delete_if_one_good_and_others_empty(my_duplicates_entire_info):

	rep_flag = 0
	hold_flag = 0
	for title in my_duplicates_entire_info:
		rep_flag = False
		hold_flag = False
		count = 0
		mms_to_save = []
		print("="*100)
		print(title)
		for mms in my_duplicates_entire_info[title][0]:
			if my_duplicates_entire_info[title][0][mms]["hold"] == '1':
				rep_flag = True
				count +=1
				if my_duplicates_entire_info[title][0][mms]["repres"] == '1':
					hold_flag =True
					mms_to_save.append(mms)
			if count>1:
				mms_to_save.append(mms)
		if rep_flag and hold_flag:
			for mms in my_duplicates_entire_info[title][0]:
				if mms not in  mms_to_save:
					my_api.delete_bib(mms)
					print("MMS to delete:",mms)
					if str(my_api.status_code).startswith("2"):
						print("deleted")
					else:
						print(my_api.xml_response_data)
						print(my_api.status_code)

				else:
					print("MMS to keep:", mms)
		elif rep_flag  and not hold_flag:
			print("#"*100)
			print("Please check if physical items were made for this title")
			print(title)
			print(my_duplicates_entire_info[title][0])
			print("#"*100)
		elif not rep_flag and hold_flag:
			print("#"*100)
			print("Please check if the title has a representation")
			print(title)
			print(my_duplicates_entire_info[title][0])
			print("#"*100)
		elif not rep_flag and not hold_flag:
			print("#"*100)
			print("Please check if the title has representation and item")
			print(title)
			print(my_duplicates_entire_info[title][0])
			print("#"*100)

		if len(mms_to_save) >1:
			print("#"*100)
			print("These titles were not deleted due to discovering of multiple representations for multiple records. Please check manually if they duplicates")
			print(title)
			print(my_duplicates_entire_info[title][0])
			print("#"*100)



def get_mark_from_file():

	my_duplicates = {}
	with open(file_name,"r", encoding = "UTF-8") as f:
		data = f.read()
	count = 0
	my_list = []
	for el in data.split("\n")[:-1]:
		if el.startswith("<?xml "):
			my_list.append(el)
			count+=1
	# print(len(my_list))
	my_new_list = list(set(my_list))
	# print(len(my_new_list))
	for el in my_new_list:
		try:
			record = parse_xml_to_array(io.StringIO(el))[0]
			# print(record)
		except:
			el = el + "</subfield></datafield></record></bib>"
			record = parse_xml_to_array(io.StringIO(el))[0]

		# print(record)
		mms_id = record["001"].value()
		title = record["245"]["a"]
		if title in my_duplicates.keys():
			my_duplicates[title] +=[mms_id]
		else:
			my_duplicates[title] = [mms_id]

	my_duplicates_entire_info={}
	for el in my_duplicates:
		small_dict = {}
		if len(my_duplicates[el])>2:
			if not "The Spinoff presents SUPERPOD" in el:
				print("#"*50)
				print(el)
				for mms in my_duplicates[el]:
					print("-"*50)
					print(mms)
					my_api.get_representations(mms,{"limit":"100"})
					try:
						rep_count = re.findall(r'count="(.*?)">',my_api.xml_response_data)[0]
					except:
						rep_count = 0
					print("Rep count: ", rep_count)
					my_api.get_holdings(mms, {"limit":"100"})
					try:
						hold_count = re.findall(r'count="(.*?)">',my_api.xml_response_data)[0]
					except:
						hold_count = 0
					print("Hold count: ",  hold_count)
					small_dict[mms] = {"hold":hold_count, "repres":rep_count}
					if el in my_duplicates_entire_info.keys():
						my_duplicates_entire_info[el]+=[small_dict]
					else:
						my_duplicates_entire_info[el]=[small_dict]
	return my_duplicates_entire_info


def main():

	set_id = "11320400410002836"
	get_records_from_set(set_id)
	my_duplicates_entire_info = None
	# my_duplicates_entire_info ={'Peter Cullinane of Lewis Road Creamery.': [{'9919081868702836': {'hold': 0, 'repres': 0}, '9919095373302836': {'hold': '1', 'repres': '1'}, '9919081972602836': {'hold': 0, 'repres': 0}}, {'9919081868702836': {'hold': 0, 'repres': 0}, '9919095373302836': {'hold': '1', 'repres': '1'}, '9919081972602836': {'hold': 0, 'repres': 0}}, {'9919081868702836': {'hold': 0, 'repres': 0}, '9919095373302836': {'hold': '1', 'repres': '1'}, '9919081972602836': {'hold': 0, 'repres': 0}}], 'Top 10 Property Podcasts To Listen and Learn From -\xa0with Ilse Wolfe': [{'9919143369702836': {'hold': 0, 'repres': 0}, '9919143367802836': {'hold': '1', 'repres': '1'}, '9919143368502836': {'hold': 0, 'repres': 0}}, {'9919143369702836': {'hold': 0, 'repres': 0}, '9919143367802836': {'hold': '1', 'repres': '1'}, '9919143368502836': {'hold': 0, 'repres': 0}}, {'9919143369702836': {'hold': 0, 'repres': 0}, '9919143367802836': {'hold': '1', 'repres': '1'}, '9919143368502836': {'hold': 0, 'repres': 0}}], 'Negative Interest Rates Are Here To Stay -\xa0What Property Investors Need to Know': [{'9919143269402836': {'hold': 0, 'repres': 0}, '9919143267202836': {'hold': '1', 'repres': '1'}, '9919143368602836': {'hold': 0, 'repres': 0}}, {'9919143269402836': {'hold': 0, 'repres': 0}, '9919143267202836': {'hold': '1', 'repres': '1'}, '9919143368602836': {'hold': 0, 'repres': 0}}, {'9919143269402836': {'hold': 0, 'repres': 0}, '9919143267202836': {'hold': '1', 'repres': '1'}, '9919143368602836': {'hold': 0, 'repres': 0}}], 'Elements 19 - Character. Rachel ONeill talks to Pip Adam about Andrea Arnolds film Milk.': [{'9919154289102836': {'hold': 0, 'repres': 0}, '9919154288702836': {'hold': 0, 'repres': 0}, '9919154288902836': {'hold': 0, 'repres': 0}, '9919154289002836': {'hold': 0, 'repres': 0}, '9919154188902836': {'hold': 0, 'repres': 0}, '9919154288502836': {'hold': '1', 'repres': '1'}, '9919154289202836': {'hold': 0, 'repres': 0}, '9919154189102836': {'hold': 0, 'repres': 0}}, {'9919154289102836': {'hold': 0, 'repres': 0}, '9919154288702836': {'hold': 0, 'repres': 0}, '9919154288902836': {'hold': 0, 'repres': 0}, '9919154289002836': {'hold': 0, 'repres': 0}, '9919154188902836': {'hold': 0, 'repres': 0}, '9919154288502836': {'hold': '1', 'repres': '1'}, '9919154289202836': {'hold': 0, 'repres': 0}, '9919154189102836': {'hold': 0, 'repres': 0}}, {'9919154289102836': {'hold': 0, 'repres': 0}, '9919154288702836': {'hold': 0, 'repres': 0}, '9919154288902836': {'hold': 0, 'repres': 0}, '9919154289002836': {'hold': 0, 'repres': 0}, '9919154188902836': {'hold': 0, 'repres': 0}, '9919154288502836': {'hold': '1', 'repres': '1'}, '9919154289202836': {'hold': 0, 'repres': 0}, '9919154189102836': {'hold': 0, 'repres': 0}}, {'9919154289102836': {'hold': 0, 'repres': 0}, '9919154288702836': {'hold': 0, 'repres': 0}, '9919154288902836': {'hold': 0, 'repres': 0}, '9919154289002836': {'hold': 0, 'repres': 0}, '9919154188902836': {'hold': 0, 'repres': 0}, '9919154288502836': {'hold': '1', 'repres': '1'}, '9919154289202836': {'hold': 0, 'repres': 0}, '9919154189102836': {'hold': 0, 'repres': 0}}, {'9919154289102836': {'hold': 0, 'repres': 0}, '9919154288702836': {'hold': 0, 'repres': 0}, '9919154288902836': {'hold': 0, 'repres': 0}, '9919154289002836': {'hold': 0, 'repres': 0}, '9919154188902836': {'hold': 0, 'repres': 0}, '9919154288502836': {'hold': '1', 'repres': '1'}, '9919154289202836': {'hold': 0, 'repres': 0}, '9919154189102836': {'hold': 0, 'repres': 0}}, {'9919154289102836': {'hold': 0, 'repres': 0}, '9919154288702836': {'hold': 0, 'repres': 0}, '9919154288902836': {'hold': 0, 'repres': 0}, '9919154289002836': {'hold': 0, 'repres': 0}, '9919154188902836': {'hold': 0, 'repres': 0}, '9919154288502836': {'hold': '1', 'repres': '1'}, '9919154289202836': {'hold': 0, 'repres': 0}, '9919154189102836': {'hold': 0, 'repres': 0}}, {'9919154289102836': {'hold': 0, 'repres': 0}, '9919154288702836': {'hold': 0, 'repres': 0}, '9919154288902836': {'hold': 0, 'repres': 0}, '9919154289002836': {'hold': 0, 'repres': 0}, '9919154188902836': {'hold': 0, 'repres': 0}, '9919154288502836': {'hold': '1', 'repres': '1'}, '9919154289202836': {'hold': 0, 'repres': 0}, '9919154189102836': {'hold': 0, 'repres': 0}}, {'9919154289102836': {'hold': 0, 'repres': 0}, '9919154288702836': {'hold': 0, 'repres': 0}, '9919154288902836': {'hold': 0, 'repres': 0}, '9919154289002836': {'hold': 0, 'repres': 0}, '9919154188902836': {'hold': 0, 'repres': 0}, '9919154288502836': {'hold': '1', 'repres': '1'}, '9919154289202836': {'hold': 0, 'repres': 0}, '9919154189102836': {'hold': 0, 'repres': 0}}], "The electrician behind 20% of NZ's new solar installations.": [{'9919143272202836': {'hold': 0, 'repres': 0}, '9919143272002836': {'hold': 0, 'repres': 0}, '9919143272302836': {'hold': 0, 'repres': 0}, '9919143272102836': {'hold': 0, 'repres': 0}, '9919143271902836': {'hold': '1', 'repres': '1'}, '9919143372302836': {'hold': 0, 'repres': 0}, '9919143372102836': {'hold': 0, 'repres': 0}, '9919143372202836': {'hold': 0, 'repres': 0}, '9919143372402836': {'hold': 0, 'repres': 0}}, {'9919143272202836': {'hold': 0, 'repres': 0}, '9919143272002836': {'hold': 0, 'repres': 0}, '9919143272302836': {'hold': 0, 'repres': 0}, '9919143272102836': {'hold': 0, 'repres': 0}, '9919143271902836': {'hold': '1', 'repres': '1'}, '9919143372302836': {'hold': 0, 'repres': 0}, '9919143372102836': {'hold': 0, 'repres': 0}, '9919143372202836': {'hold': 0, 'repres': 0}, '9919143372402836': {'hold': 0, 'repres': 0}}, {'9919143272202836': {'hold': 0, 'repres': 0}, '9919143272002836': {'hold': 0, 'repres': 0}, '9919143272302836': {'hold': 0, 'repres': 0}, '9919143272102836': {'hold': 0, 'repres': 0}, '9919143271902836': {'hold': '1', 'repres': '1'}, '9919143372302836': {'hold': 0, 'repres': 0}, '9919143372102836': {'hold': 0, 'repres': 0}, '9919143372202836': {'hold': 0, 'repres': 0}, '9919143372402836': {'hold': 0, 'repres': 0}}, {'9919143272202836': {'hold': 0, 'repres': 0}, '9919143272002836': {'hold': 0, 'repres': 0}, '9919143272302836': {'hold': 0, 'repres': 0}, '9919143272102836': {'hold': 0, 'repres': 0}, '9919143271902836': {'hold': '1', 'repres': '1'}, '9919143372302836': {'hold': 0, 'repres': 0}, '9919143372102836': {'hold': 0, 'repres': 0}, '9919143372202836': {'hold': 0, 'repres': 0}, '9919143372402836': {'hold': 0, 'repres': 0}}, {'9919143272202836': {'hold': 0, 'repres': 0}, '9919143272002836': {'hold': 0, 'repres': 0}, '9919143272302836': {'hold': 0, 'repres': 0}, '9919143272102836': {'hold': 0, 'repres': 0}, '9919143271902836': {'hold': '1', 'repres': '1'}, '9919143372302836': {'hold': 0, 'repres': 0}, '9919143372102836': {'hold': 0, 'repres': 0}, '9919143372202836': {'hold': 0, 'repres': 0}, '9919143372402836': {'hold': 0, 'repres': 0}}, {'9919143272202836': {'hold': 0, 'repres': 0}, '9919143272002836': {'hold': 0, 'repres': 0}, '9919143272302836': {'hold': 0, 'repres': 0}, '9919143272102836': {'hold': 0, 'repres': 0}, '9919143271902836': {'hold': '1', 'repres': '1'}, '9919143372302836': {'hold': 0, 'repres': 0}, '9919143372102836': {'hold': 0, 'repres': 0}, '9919143372202836': {'hold': 0, 'repres': 0}, '9919143372402836': {'hold': 0, 'repres': 0}}, {'9919143272202836': {'hold': 0, 'repres': 0}, '9919143272002836': {'hold': 0, 'repres': 0}, '9919143272302836': {'hold': 0, 'repres': 0}, '9919143272102836': {'hold': 0, 'repres': 0}, '9919143271902836': {'hold': '1', 'repres': '1'}, '9919143372302836': {'hold': 0, 'repres': 0}, '9919143372102836': {'hold': 0, 'repres': 0}, '9919143372202836': {'hold': 0, 'repres': 0}, '9919143372402836': {'hold': 0, 'repres': 0}}, {'9919143272202836': {'hold': 0, 'repres': 0}, '9919143272002836': {'hold': 0, 'repres': 0}, '9919143272302836': {'hold': 0, 'repres': 0}, '9919143272102836': {'hold': 0, 'repres': 0}, '9919143271902836': {'hold': '1', 'repres': '1'}, '9919143372302836': {'hold': 0, 'repres': 0}, '9919143372102836': {'hold': 0, 'repres': 0}, '9919143372202836': {'hold': 0, 'repres': 0}, '9919143372402836': {'hold': 0, 'repres': 0}}, {'9919143272202836': {'hold': 0, 'repres': 0}, '9919143272002836': {'hold': 0, 'repres': 0}, '9919143272302836': {'hold': 0, 'repres': 0}, '9919143272102836': {'hold': 0, 'repres': 0}, '9919143271902836': {'hold': '1', 'repres': '1'}, '9919143372302836': {'hold': 0, 'repres': 0}, '9919143372102836': {'hold': 0, 'repres': 0}, '9919143372202836': {'hold': 0, 'repres': 0}, '9919143372402836': {'hold': 0, 'repres': 0}}], 'Investment Build NZ Review -\xa0Should I Buy an Investment Property Through Them?': [{'9919143367702836': {'hold': '1', 'repres': '1'}, '9919143267902836': {'hold': 0, 'repres': 0}, '9919143369402836': {'hold': 0, 'repres': 0}}, {'9919143367702836': {'hold': '1', 'repres': '1'}, '9919143267902836': {'hold': 0, 'repres': 0}, '9919143369402836': {'hold': 0, 'repres': 0}}, {'9919143367702836': {'hold': '1', 'repres': '1'}, '9919143267902836': {'hold': 0, 'repres': 0}, '9919143369402836': {'hold': 0, 'repres': 0}}], 'Govt. To Buy Properties In Partnership With First Home Buyers -\xa0Part #2': [{'9919143270102836': {'hold': 0, 'repres': 0}, '9919143368802836': {'hold': 0, 'repres': 0}, '9919143267302836': {'hold': '1', 'repres': '1'}}, {'9919143270102836': {'hold': 0, 'repres': 0}, '9919143368802836': {'hold': 0, 'repres': 0}, '9919143267302836': {'hold': '1', 'repres': '1'}}, {'9919143270102836': {'hold': 0, 'repres': 0}, '9919143368802836': {'hold': 0, 'repres': 0}, '9919143267302836': {'hold': '1', 'repres': '1'}}], "Oliver Mander from the NZ Shareholders' Association NZSA.": [{'9919154181002836': {'hold': 0, 'repres': 0}, '9919154280102836': {'hold': 0, 'repres': 0}, '9919154179802836': {'hold': '1', 'repres': '1'}}, {'9919154181002836': {'hold': 0, 'repres': 0}, '9919154280102836': {'hold': 0, 'repres': 0}, '9919154179802836': {'hold': '1', 'repres': '1'}}, {'9919154181002836': {'hold': 0, 'repres': 0}, '9919154280102836': {'hold': 0, 'repres': 0}, '9919154179802836': {'hold': '1', 'repres': '1'}}], 'Govt. To Buy Properties In Partnership With First Home Buyers -\xa0Part #1': [{'9919143368002836': {'hold': '1', 'repres': '1'}, '9919143268202836': {'hold': 0, 'repres': 0}, '9919143270002836': {'hold': 0, 'repres': 0}}, {'9919143368002836': {'hold': '1', 'repres': '1'}, '9919143268202836': {'hold': 0, 'repres': 0}, '9919143270002836': {'hold': 0, 'repres': 0}}, {'9919143368002836': {'hold': '1', 'repres': '1'}, '9919143268202836': {'hold': 0, 'repres': 0}, '9919143270002836': {'hold': 0, 'repres': 0}}], 'New LVR Rules Threaten First Home Buyers - But Is It a Big Deal?': [{'9919143369302836': {'hold': 0, 'repres': 0}, '9919143367502836': {'hold': '1', 'repres': '1'}, '9919143368302836': {'hold': 0, 'repres': 0}}, {'9919143369302836': {'hold': 0, 'repres': 0}, '9919143367502836': {'hold': '1', 'repres': '1'}, '9919143368302836': {'hold': 0, 'repres': 0}}, {'9919143369302836': {'hold': 0, 'repres': 0}, '9919143367502836': {'hold': '1', 'repres': '1'}, '9919143368302836': {'hold': 0, 'repres': 0}}], 'Elements 18 - Point. Kirsten McDougall talks to Pip Adam about first-person perspective.': [{'9919154288802836': {'hold': 0, 'repres': 0}, '9919154189002836': {'hold': 0, 'repres': 0}, '9919154188702836': {'hold': 0, 'repres': 0}, '9919154188602836': {'hold': 0, 'repres': 0}, '9919154188802836': {'hold': 0, 'repres': 0}, '9919154289402836': {'hold': 0, 'repres': 0}, '9919154289302836': {'hold': 0, 'repres': 0}, '9919154288402836': {'hold': '1', 'repres': '1'}, '9919154288602836': {'hold': 0, 'repres': 0}}, {'9919154288802836': {'hold': 0, 'repres': 0}, '9919154189002836': {'hold': 0, 'repres': 0}, '9919154188702836': {'hold': 0, 'repres': 0}, '9919154188602836': {'hold': 0, 'repres': 0}, '9919154188802836': {'hold': 0, 'repres': 0}, '9919154289402836': {'hold': 0, 'repres': 0}, '9919154289302836': {'hold': 0, 'repres': 0}, '9919154288402836': {'hold': '1', 'repres': '1'}, '9919154288602836': {'hold': 0, 'repres': 0}}, {'9919154288802836': {'hold': 0, 'repres': 0}, '9919154189002836': {'hold': 0, 'repres': 0}, '9919154188702836': {'hold': 0, 'repres': 0}, '9919154188602836': {'hold': 0, 'repres': 0}, '9919154188802836': {'hold': 0, 'repres': 0}, '9919154289402836': {'hold': 0, 'repres': 0}, '9919154289302836': {'hold': 0, 'repres': 0}, '9919154288402836': {'hold': '1', 'repres': '1'}, '9919154288602836': {'hold': 0, 'repres': 0}}, {'9919154288802836': {'hold': 0, 'repres': 0}, '9919154189002836': {'hold': 0, 'repres': 0}, '9919154188702836': {'hold': 0, 'repres': 0}, '9919154188602836': {'hold': 0, 'repres': 0}, '9919154188802836': {'hold': 0, 'repres': 0}, '9919154289402836': {'hold': 0, 'repres': 0}, '9919154289302836': {'hold': 0, 'repres': 0}, '9919154288402836': {'hold': '1', 'repres': '1'}, '9919154288602836': {'hold': 0, 'repres': 0}}, {'9919154288802836': {'hold': 0, 'repres': 0}, '9919154189002836': {'hold': 0, 'repres': 0}, '9919154188702836': {'hold': 0, 'repres': 0}, '9919154188602836': {'hold': 0, 'repres': 0}, '9919154188802836': {'hold': 0, 'repres': 0}, '9919154289402836': {'hold': 0, 'repres': 0}, '9919154289302836': {'hold': 0, 'repres': 0}, '9919154288402836': {'hold': '1', 'repres': '1'}, '9919154288602836': {'hold': 0, 'repres': 0}}, {'9919154288802836': {'hold': 0, 'repres': 0}, '9919154189002836': {'hold': 0, 'repres': 0}, '9919154188702836': {'hold': 0, 'repres': 0}, '9919154188602836': {'hold': 0, 'repres': 0}, '9919154188802836': {'hold': 0, 'repres': 0}, '9919154289402836': {'hold': 0, 'repres': 0}, '9919154289302836': {'hold': 0, 'repres': 0}, '9919154288402836': {'hold': '1', 'repres': '1'}, '9919154288602836': {'hold': 0, 'repres': 0}}, {'9919154288802836': {'hold': 0, 'repres': 0}, '9919154189002836': {'hold': 0, 'repres': 0}, '9919154188702836': {'hold': 0, 'repres': 0}, '9919154188602836': {'hold': 0, 'repres': 0}, '9919154188802836': {'hold': 0, 'repres': 0}, '9919154289402836': {'hold': 0, 'repres': 0}, '9919154289302836': {'hold': 0, 'repres': 0}, '9919154288402836': {'hold': '1', 'repres': '1'}, '9919154288602836': {'hold': 0, 'repres': 0}}, {'9919154288802836': {'hold': 0, 'repres': 0}, '9919154189002836': {'hold': 0, 'repres': 0}, '9919154188702836': {'hold': 0, 'repres': 0}, '9919154188602836': {'hold': 0, 'repres': 0}, '9919154188802836': {'hold': 0, 'repres': 0}, '9919154289402836': {'hold': 0, 'repres': 0}, '9919154289302836': {'hold': 0, 'repres': 0}, '9919154288402836': {'hold': '1', 'repres': '1'}, '9919154288602836': {'hold': 0, 'repres': 0}}, {'9919154288802836': {'hold': 0, 'repres': 0}, '9919154189002836': {'hold': 0, 'repres': 0}, '9919154188702836': {'hold': 0, 'repres': 0}, '9919154188602836': {'hold': 0, 'repres': 0}, '9919154188802836': {'hold': 0, 'repres': 0}, '9919154289402836': {'hold': 0, 'repres': 0}, '9919154289302836': {'hold': 0, 'repres': 0}, '9919154288402836': {'hold': '1', 'repres': '1'}, '9919154288602836': {'hold': 0, 'repres': 0}}], "Breaking: Govt Announces New Tax Details - Here's What Is and Isn't Included": [{'9919143267802836': {'hold': 0, 'repres': 0}, '9919143268702836': {'hold': 0, 'repres': 0}, '9919143367602836': {'hold': '1', 'repres': '1'}}, {'9919143267802836': {'hold': 0, 'repres': 0}, '9919143268702836': {'hold': 0, 'repres': 0}, '9919143367602836': {'hold': '1', 'repres': '1'}}, {'9919143267802836': {'hold': 0, 'repres': 0}, '9919143268702836': {'hold': 0, 'repres': 0}, '9919143367602836': {'hold': '1', 'repres': '1'}}], "Residents Association vs Body Corporates - What's The Difference? What's the Cost?": [{'9919121706502836': {'hold': 0, 'repres': 0}, '9919121705202836': {'hold': '1', 'repres': '1'}, '9919121606802836': {'hold': 0, 'repres': 0}}, {'9919121706502836': {'hold': 0, 'repres': 0}, '9919121705202836': {'hold': '1', 'repres': '1'}, '9919121606802836': {'hold': 0, 'repres': 0}}, {'9919121706502836': {'hold': 0, 'repres': 0}, '9919121705202836': {'hold': '1', 'repres': '1'}, '9919121606802836': {'hold': 0, 'repres': 0}}], 'Social + Public Housing - New Tax Incentives Announced That Will Save You Thousands': [{'9919143269302836': {'hold': 0, 'repres': 0}, '9919143268102836': {'hold': 0, 'repres': 0}, '9919143267102836': {'hold': '1', 'repres': '1'}}, {'9919143269302836': {'hold': 0, 'repres': 0}, '9919143268102836': {'hold': 0, 'repres': 0}, '9919143267102836': {'hold': '1', 'repres': '1'}}, {'9919143269302836': {'hold': 0, 'repres': 0}, '9919143268102836': {'hold': 0, 'repres': 0}, '9919143267102836': {'hold': '1', 'repres': '1'}}], 'First Home Buyer Case Studies - Stories Of People Who Are Actually Doing It': [{'9919143268302836': {'hold': 0, 'repres': 0}, '9919143270202836': {'hold': 0, 'repres': 0}, '9919143368102836': {'hold': '1', 'repres': '1'}}, {'9919143268302836': {'hold': 0, 'repres': 0}, '9919143270202836': {'hold': 0, 'repres': 0}, '9919143368102836': {'hold': '1', 'repres': '1'}}, {'9919143268302836': {'hold': 0, 'repres': 0}, '9919143270202836': {'hold': 0, 'repres': 0}, '9919143368102836': {'hold': '1', 'repres': '1'}}], 'Marianne Elliott.': [{'9919009337702836': {'hold': 0, 'repres': 0}, '9919009244502836': {'hold': 0, 'repres': 0}, '9919009248202836': {'hold': 0, 'repres': 0}, '9919006461202836': {'hold': 0, 'repres': 0}, '9919009361802836': {'hold': 0, 'repres': 0}, '9919009252202836': {'hold': 0, 'repres': 0}, '9919009352302836': {'hold': 0, 'repres': 0}, '9919015272002836': {'hold': '1', 'repres': '1'}}, {'9919009337702836': {'hold': 0, 'repres': 0}, '9919009244502836': {'hold': 0, 'repres': 0}, '9919009248202836': {'hold': 0, 'repres': 0}, '9919006461202836': {'hold': 0, 'repres': 0}, '9919009361802836': {'hold': 0, 'repres': 0}, '9919009252202836': {'hold': 0, 'repres': 0}, '9919009352302836': {'hold': 0, 'repres': 0}, '9919015272002836': {'hold': '1', 'repres': '1'}}, {'9919009337702836': {'hold': 0, 'repres': 0}, '9919009244502836': {'hold': 0, 'repres': 0}, '9919009248202836': {'hold': 0, 'repres': 0}, '9919006461202836': {'hold': 0, 'repres': 0}, '9919009361802836': {'hold': 0, 'repres': 0}, '9919009252202836': {'hold': 0, 'repres': 0}, '9919009352302836': {'hold': 0, 'repres': 0}, '9919015272002836': {'hold': '1', 'repres': '1'}}, {'9919009337702836': {'hold': 0, 'repres': 0}, '9919009244502836': {'hold': 0, 'repres': 0}, '9919009248202836': {'hold': 0, 'repres': 0}, '9919006461202836': {'hold': 0, 'repres': 0}, '9919009361802836': {'hold': 0, 'repres': 0}, '9919009252202836': {'hold': 0, 'repres': 0}, '9919009352302836': {'hold': 0, 'repres': 0}, '9919015272002836': {'hold': '1', 'repres': '1'}}, {'9919009337702836': {'hold': 0, 'repres': 0}, '9919009244502836': {'hold': 0, 'repres': 0}, '9919009248202836': {'hold': 0, 'repres': 0}, '9919006461202836': {'hold': 0, 'repres': 0}, '9919009361802836': {'hold': 0, 'repres': 0}, '9919009252202836': {'hold': 0, 'repres': 0}, '9919009352302836': {'hold': 0, 'repres': 0}, '9919015272002836': {'hold': '1', 'repres': '1'}}, {'9919009337702836': {'hold': 0, 'repres': 0}, '9919009244502836': {'hold': 0, 'repres': 0}, '9919009248202836': {'hold': 0, 'repres': 0}, '9919006461202836': {'hold': 0, 'repres': 0}, '9919009361802836': {'hold': 0, 'repres': 0}, '9919009252202836': {'hold': 0, 'repres': 0}, '9919009352302836': {'hold': 0, 'repres': 0}, '9919015272002836': {'hold': '1', 'repres': '1'}}, {'9919009337702836': {'hold': 0, 'repres': 0}, '9919009244502836': {'hold': 0, 'repres': 0}, '9919009248202836': {'hold': 0, 'repres': 0}, '9919006461202836': {'hold': 0, 'repres': 0}, '9919009361802836': {'hold': 0, 'repres': 0}, '9919009252202836': {'hold': 0, 'repres': 0}, '9919009352302836': {'hold': 0, 'repres': 0}, '9919015272002836': {'hold': '1', 'repres': '1'}}, {'9919009337702836': {'hold': 0, 'repres': 0}, '9919009244502836': {'hold': 0, 'repres': 0}, '9919009248202836': {'hold': 0, 'repres': 0}, '9919006461202836': {'hold': 0, 'repres': 0}, '9919009361802836': {'hold': 0, 'repres': 0}, '9919009252202836': {'hold': 0, 'repres': 0}, '9919009352302836': {'hold': 0, 'repres': 0}, '9919015272002836': {'hold': '1', 'repres': '1'}}], "It's Our 2nd Year Anniversary -\xa0What We've Learnt Over the Last 2 Years in Property": [{'9919121706602836': {'hold': 0, 'repres': 0}, '9919121606302836': {'hold': '1', 'repres': '1'}, '9919121607002836': {'hold': 0, 'repres': 0}}, {'9919121706602836': {'hold': 0, 'repres': 0}, '9919121606302836': {'hold': '1', 'repres': '1'}, '9919121607002836': {'hold': 0, 'repres': 0}}, {'9919121706602836': {'hold': 0, 'repres': 0}, '9919121606302836': {'hold': '1', 'repres': '1'}, '9919121607002836': {'hold': 0, 'repres': 0}}], 'Book Review: Only Woman in the Room - 20 Stories of 20 Female Property Investors': [{'9919143269102836': {'hold': 0, 'repres': 0}, '9919143267002836': {'hold': '1', 'repres': '1'}, '9919143268002836': {'hold': 0, 'repres': 0}}, {'9919143269102836': {'hold': 0, 'repres': 0}, '9919143267002836': {'hold': '1', 'repres': '1'}, '9919143268002836': {'hold': 0, 'repres': 0}}, {'9919143269102836': {'hold': 0, 'repres': 0}, '9919143267002836': {'hold': '1', 'repres': '1'}, '9919143268002836': {'hold': 0, 'repres': 0}}], 'Invercargill - Is It a Good Place to Invest? What Property Investors Need to Know': [{'9919143267702836': {'hold': 0, 'repres': 0}, '9919143367302836': {'hold': '1', 'repres': '1'}, '9919143268402836': {'hold': 0, 'repres': 0}}, {'9919143267702836': {'hold': 0, 'repres': 0}, '9919143367302836': {'hold': '1', 'repres': '1'}, '9919143268402836': {'hold': 0, 'repres': 0}}, {'9919143267702836': {'hold': 0, 'repres': 0}, '9919143367302836': {'hold': '1', 'repres': '1'}, '9919143268402836': {'hold': 0, 'repres': 0}}], 'Bonus Episode: How to Build + Plan a Property Investment Portfolio - Webinar audio.': [{'9919143269802836': {'hold': 0, 'repres': 0}, '9919143367902836': {'hold': '1', 'repres': '1'}, '9919143368702836': {'hold': 0, 'repres': 0}}, {'9919143269802836': {'hold': 0, 'repres': 0}, '9919143367902836': {'hold': '1', 'repres': '1'}, '9919143368702836': {'hold': 0, 'repres': 0}}, {'9919143269802836': {'hold': 0, 'repres': 0}, '9919143367902836': {'hold': '1', 'repres': '1'}, '9919143368702836': {'hold': 0, 'repres': 0}}], "Removing the fill' from landfill!": [{'9919154290002836': {'hold': 0, 'repres': 0}, '9919154190002836': {'hold': 0, 'repres': 0}, '9919154289802836': {'hold': '1', 'repres': '1'}, '9919154289902836': {'hold': 0, 'repres': 0}}, {'9919154290002836': {'hold': 0, 'repres': 0}, '9919154190002836': {'hold': 0, 'repres': 0}, '9919154289802836': {'hold': '1', 'repres': '1'}, '9919154289902836': {'hold': 0, 'repres': 0}}, {'9919154290002836': {'hold': 0, 'repres': 0}, '9919154190002836': {'hold': 0, 'repres': 0}, '9919154289802836': {'hold': '1', 'repres': '1'}, '9919154289902836': {'hold': 0, 'repres': 0}}, {'9919154290002836': {'hold': 0, 'repres': 0}, '9919154190002836': {'hold': 0, 'repres': 0}, '9919154289802836': {'hold': '1', 'repres': '1'}, '9919154289902836': {'hold': 0, 'repres': 0}}], "China's Largest Developer Almost Bankrupt -\xa0Evergrande + The Impact On NZ Property Investors?": [{'9919143368402836': {'hold': 0, 'repres': 0}, '9919143266902836': {'hold': '1', 'repres': '1'}, '9919143268802836': {'hold': 0, 'repres': 0}}, {'9919143368402836': {'hold': 0, 'repres': 0}, '9919143266902836': {'hold': '1', 'repres': '1'}, '9919143268802836': {'hold': 0, 'repres': 0}}, {'9919143368402836': {'hold': 0, 'repres': 0}, '9919143266902836': {'hold': '1', 'repres': '1'}, '9919143268802836': {'hold': 0, 'repres': 0}}], 'Ruth Croft.': [{'9919006463402836': {'hold': '1', 'repres': '1'}, '9919015272302836': {'hold': '1', 'repres': '1'}, '9919054572002836': {'hold': '1', 'repres': '1'}}, {'9919006463402836': {'hold': '1', 'repres': '1'}, '9919015272302836': {'hold': '1', 'repres': '1'}, '9919054572002836': {'hold': '1', 'repres': '1'}}, {'9919006463402836': {'hold': '1', 'repres': '1'}, '9919015272302836': {'hold': '1', 'repres': '1'}, '9919054572002836': {'hold': '1', 'repres': '1'}}], 'Case Study - "Which One do I Sell?" - A Look Into This Experienced Investor\'s Portfolio': [{'9919143369202836': {'hold': 0, 'repres': 0}, '9919143367402836': {'hold': '1', 'repres': '1'}, '9919143368202836': {'hold': 0, 'repres': 0}}, {'9919143369202836': {'hold': 0, 'repres': 0}, '9919143367402836': {'hold': '1', 'repres': '1'}, '9919143368202836': {'hold': 0, 'repres': 0}}, {'9919143369202836': {'hold': 0, 'repres': 0}, '9919143367402836': {'hold': '1', 'repres': '1'}, '9919143368202836': {'hold': 0, 'repres': 0}}]}
	if not my_duplicates_entire_info:
		my_duplicates_entire_info = get_mark_from_file()
	print(my_duplicates_entire_info)
	# delete_if_one_good_and_others_empty(my_duplicates_entire_info)

if __name__ == '__main__':
	main()