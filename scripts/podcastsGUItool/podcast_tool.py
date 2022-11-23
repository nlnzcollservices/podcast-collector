import os
import io
import re
import wget
import shutil
import requests
import urllib
import PySimpleGUI as sg
from pathlib import Path
from pymarc import parse_xml_to_array,record_to_xml,Field
from datetime import datetime as dt
from bs4 import BeautifulSoup as bs
from rosetta_sip_factory.sip_builder import build_sip
from description_maker import make_description
#against ssl errors during wget
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import random
try:
	from api_file import apikey
except:
	pass
from podcast_dict import podcasts_dict
username = os.environ.get("USERNAME")
api_key = None
if not apikey:
	apikey = ""
out_folder = r"C:\Users\{}\podast_files".format(username)
sip_out_folder =r"C:\Users\{}\podcast_sip".format(username)
headers = {'content-type': 'application/xml'}

# import description_maker
# from issuu_image_dict import issuu_dict
# from my_settings import sip_folder, to_send_email, file_folder, email_address_line, report_folder_images, template_folder,logging, rosetta_folder, seas_dict, term_dict, months, reversed_season, months_dictionary,short_month_dict, not_processed_files

# sys.path.insert(0,r'Y:\ndha\pre-deposit_prod\LD_working\podcasts\scripts')
# from alma_tools import AlmaTools
def my_gui(values = None):
	"""
	This function running form in separate window and collect values
	Returns:
		values(dict) - dictionary of form values
	"""
	value_list  = ["OneOffIE","PeriodicIE"]

	if not values:
		initial_alma_mms ='mis MMS id'
		initial_alma_mms_serial ='serial MMS id'
		initial_podc_name = ""
		initial_ep_title = "Episode title"
		initial_url = r'https://static1.squarespace.com/static/5b12367ff8370a538dd229e3/t/5efaf3b27c5dc01882c95d91/1593505625645/ep+99+Robbie+Britton.mp3'
		initial_output = str(out_folder)
		initial_output_sip = str(sip_out_folder)
		initial_942 = 	"nbnz {}".format(str(dt.now().strftime( '%Y-%m')))
		initial_rights = "100"
		initial_entity = ""
		initial_enum_a = ""
		initial_enum_b= ""
		initial_enum_c = ""
		initial_chron_i = ""
		initial_chron_j = ""
		initial_chron_k = ""
		initial_pol = ''
		initial_api=''



	else:
		initial_alma_mms =values['mms_id']
		initial_podc_name = values['podc_name']
		initial_ep_title = values["ep_title"]
		initial_url = values['url']
		initial_942 = values['field942']
		initial_output = values["output_folder"]
		initial_output_sip = values["output_sip_folder"]
		initial_entity = values["entity_type"]
		initial_rights = values['access']
		initial_enum_a = values["enum_a"]
		initial_enum_b = values["enum_b"]
		initial_enum_c = values["enum_c"]
		initial_chron_i = values["chron_i"]
		initial_chron_j = values["chron_j"]
		initial_chron_k = values["chron_k"]
		initial_pol = values['serial_po_line']
		initial_api=values['api_key']





	form = sg.FlexForm('Simple SIP form')
	schemes = ["BlueMono","Tan","BluePurple","LightBrown","SystemDefaultForReal","LightBrown18","LightBrown16","LightBrown15","LightBrown14","LightBrown12","LightBrown11","LightBrown10","LightBrown8","LightBrown7","LightBrown6","LightBrown9","LightBrown5","Kayak","Purple","DarkGreen1","DarkGreen2","DarkGreen3","TealMono","Python","LightGrey3","LightGrey6","SendyBeach","BluePurple","DarkTeal7","LightGreen2",'DarkBrown6','Purple','DarkGreen4','DarkTeal7']
	#all_schemes = ['Black', 'BlueMono', 'BluePurple', 'BrightColors', 'BrownBlue', 'Dark', 'Dark2', 'DarkAmber', 'DarkBlack', 'DarkBlack1', 'DarkBlue', 'DarkBlue1', 'DarkBlue10', 'DarkBlue11', 'DarkBlue12', 'DarkBlue13', 'DarkBlue14', 'DarkBlue15', 'DarkBlue16', 'DarkBlue17', 'DarkBlue2', 'DarkBlue3', 'DarkBlue4', 'DarkBlue5', 'DarkBlue6', 'DarkBlue7', 'DarkBlue8', 'DarkBlue9', 'DarkBrown', 'DarkBrown1', 'DarkBrown2', 'DarkBrown3', 'DarkBrown4', 'DarkBrown5', 'DarkBrown6', 'DarkBrown7', 'DarkGreen', 'DarkGreen1', 'DarkGreen2', 'DarkGreen3', 'DarkGreen4', 'DarkGreen5', 'DarkGreen6', 'DarkGreen7', 'DarkGrey', 'DarkGrey1', 'DarkGrey10', 'DarkGrey11', 'DarkGrey12', 'DarkGrey13', 'DarkGrey14', 'DarkGrey2', 'DarkGrey3', 'DarkGrey4', 'DarkGrey5', 'DarkGrey6', 'DarkGrey7', 'DarkGrey8', 'DarkGrey9', 'DarkPurple', 'DarkPurple1', 'DarkPurple2', 'DarkPurple3', 'DarkPurple4', 'DarkPurple5', 'DarkPurple6', 'DarkPurple7', 'DarkRed', 'DarkRed1', 'DarkRed2', 'DarkTanBlue', 'DarkTeal', 'DarkTeal1', 'DarkTeal10', 'DarkTeal11', 'DarkTeal12', 'DarkTeal2', 'DarkTeal3', 'DarkTeal4', 'DarkTeal5', 'DarkTeal6', 'DarkTeal7', 'DarkTeal8', 'DarkTeal9', 'Default', 'Default1', 'DefaultNoMoreNagging', 'GrayGrayGray', 'Green', 'GreenMono', 'GreenTan', 'HotDogStand', 'Kayak', 'LightBlue', 'LightBlue1', 'LightBlue2', 'LightBlue3', 'LightBlue4', 'LightBlue5', 'LightBlue6', 'LightBlue7', 'LightBrown', 'LightBrown1', 'LightBrown10', 'LightBrown11', 'LightBrown12', 'LightBrown13', 'LightBrown2', 'LightBrown3', 'LightBrown4', 'LightBrown5', 'LightBrown6', 'LightBrown7', 'LightBrown8', 'LightBrown9', 'LightGray1', 'LightGreen', 'LightGreen1', 'LightGreen10', 'LightGreen2', 'LightGreen3', 'LightGreen4', 'LightGreen5', 'LightGreen6', 'LightGreen7', 'LightGreen8', 'LightGreen9', 'LightGrey', 'LightGrey1', 'LightGrey2', 'LightGrey3', 'LightGrey4', 'LightGrey5', 'LightGrey6', 'LightPurple', 'LightTeal', 'LightYellow', 'Material1', 'Material2', 'NeutralBlue', 'Purple', 'Python', 'Reddit', 'Reds', 'SandyBeach', 'SystemDefault', 'SystemDefault1', 'SystemDefaultForReal', 'Tan', 'TanBlue', 'TealMono', 'Topanga']
	all_schemes = ['Black', 'BlueMono', 'BluePurple', 'BrightColors', 'BrownBlue', 'Dark', 'Dark2', 'DarkAmber', 'DarkBlack', 'DarkBlack1', 'DarkBlue', 'DarkBlue1', 'DarkBlue10', 'DarkBlue11', 'DarkBlue12', 'DarkBlue13', 'DarkBlue14', 'DarkBlue15', 'DarkBlue16', 'DarkBlue17', 'DarkBlue2', 'DarkBlue3', 'DarkBlue4', 'DarkBlue5', 'DarkBlue6', 'DarkBlue7', 'DarkBlue8', 'DarkBlue9', 'DarkBrown', 'DarkBrown1', 'DarkBrown2', 'DarkBrown3', 'DarkBrown4', 'DarkBrown5', 'DarkBrown6', 'DarkBrown7', 'DarkGreen', 'DarkGreen1', 'DarkGreen2', 'DarkGreen3', 'DarkGreen4', 'DarkGreen5', 'DarkGreen6', 'DarkGreen7', 'DarkGrey', 'DarkGrey1', 'DarkGrey10', 'DarkGrey11', 'DarkGrey12', 'DarkGrey13', 'DarkGrey14', 'DarkGrey2', 'DarkGrey3', 'DarkGrey4', 'DarkGrey5', 'DarkGrey6', 'DarkGrey7', 'DarkGrey8', 'DarkGrey9', 'DarkPurple', 'DarkPurple1', 'DarkPurple2', 'DarkPurple3', 'DarkPurple4', 'DarkPurple5', 'DarkPurple6', 'DarkPurple7', 'DarkRed', 'DarkRed1', 'DarkRed2', 'DarkTanBlue', 'DarkTeal', 'DarkTeal1', 'DarkTeal10', 'DarkTeal11', 'DarkTeal12', 'DarkTeal2', 'DarkTeal3', 'DarkTeal4', 'DarkTeal5', 'DarkTeal6', 'DarkTeal7', 'DarkTeal8', 'DarkTeal9', 'Default', 'Default1', 'DefaultNoMoreNagging', 'GrayGrayGray', 'Green', 'GreenMono', 'GreenTan', 'HotDogStand', 'Kayak', 'LightBlue', 'LightBlue1', 'LightBlue2', 'LightBlue3', 'LightBlue4', 'LightBlue5', 'LightBlue6', 'LightBlue7', 'LightBrown', 'LightBrown1', 'LightBrown10', 'LightBrown11', 'LightBrown12', 'LightBrown13', 'LightBrown2', 'LightBrown3', 'LightBrown4', 'LightBrown5', 'LightBrown6', 'LightBrown7', 'LightBrown8', 'LightBrown9', 'LightGray1', 'LightGreen', 'LightGreen1', 'LightGreen10', 'LightGreen2', 'LightGreen3', 'LightGreen4', 'LightGreen5', 'LightGreen6', 'LightGreen7', 'LightGreen8', 'LightGreen9', 'LightGrey', 'LightGrey1', 'LightGrey2', 'LightGrey3', 'LightGrey4', 'LightGrey5', 'LightGrey6', 'LightPurple', 'LightTeal', 'LightYellow', 'Material1', 'Material2', 'NeutralBlue', 'Purple', 'Python', 'Reddit', 'Reds', 'SandyBeach', 'SystemDefault', 'SystemDefault1', 'SystemDefaultForReal', 'Tan', 'TanBlue', 'TealMono', 'Topanga']

	#all_schemes =["LightBlue2",'LightGrey2',"GrayGrayGray","Default1"]
	# sg.theme("BlueMono")
	# sg.theme("Tan")
	# sg.theme("BluePurple")
	# sg.theme("LightBrown")
	# sg.theme("SystemDefaultForReal")
	# sg.theme("LightBrown18")
	# sg.theme("LightBrown16")
	# sg.theme("LightBrown15")
	# sg.theme("LightBrown14")
	# sg.theme("LightBrown12")
	# sg.theme("LightBrown11")
	# sg.theme("LightBrown10")
	# sg.theme("LightBrown8")
	# sg.theme("LightBrown7")
	#sg.theme("LightBrown6")
	#sg.theme("LightBrown9")
	#sg.theme("LightBrown5")
	#sg.theme("Kayak")
	# sg.theme("Purple")
	# sg.theme("DarkGreen1")
	# sg.theme("DarkGreen2")
	# sg.theme("DarkGreen3")
	# sg.theme("TealMono")
	# sg.theme("Python")
	#sg.theme("LightGrey3")
	# sg.theme("LightGrey6")
	#sg.theme("SendyBeach")
	r = random.choice(all_schemes)
	sg.theme(r)


	

	layout = [

			[sg.Text('Insert episode details')],

			[sg.Text('Alma MMS mono', size=(17, 1)), sg.InputText(initial_alma_mms,key='mms_id',size=(35, 1))],
			[sg.Text('Podcast name', size=(17, 1)), sg.InputText(initial_podc_name,key='podc_name', size=(35, 1))],
			[sg.Text('Episode title', size=(17, 1)), sg.InputText(initial_ep_title,key='ep_title', size=(35, 1))],
			[sg.Checkbox('Download?', default=False,key='if_download', font = ('Helvetica', 15, 'bold italic'))],
			[sg.Text('episode URL', size=(17, 1)), sg.InputText(initial_url,key='url',size=(35, 1))],
			[sg.Text('Files output folder (opt)', size=(17, 1)), sg.InputText(initial_output,key = "output_folder", size=(50, 1))],
			[sg.Checkbox('Make SIP?', default=False,key='if_sip',font = ('Helvetica', 15, 'bold italic'))],
			[sg.Text('Output SIP folder (opt)', size=(17, 1)), sg.InputText(initial_output_sip,key = "output_sip_folder", size=(50, 1))],
			[sg.Text('Entity type',size=(17, 1)), sg.Listbox(values=value_list, size=(30, 1), default_values=initial_entity, key='entity_type')],
			[sg.Text('Policy ID', size=(17, 1)), sg.InputText(initial_rights,key='access',size=(5, 1))],
			[sg.Text('enumerationA (volume)', size=(10, 2)), sg.InputText(initial_enum_a,key="enum_a",size=(5, 1)),sg.Text('enumerationB (number)', size=(10, 2)), sg.InputText(initial_enum_b,key="enum_b",size=(5, 1)),sg.Text('enumerationC (issue)', size=(10, 2)), sg.InputText(initial_enum_c,key="enum_c",size=(5, 1))],
			[sg.Text('chronology I (year)', size=(10, 2)), sg.InputText(initial_chron_i,key="chron_i",size=(5, 1)),sg.Text('chronology J (month)', size=(10, 2)), sg.InputText(initial_chron_j,key="chron_j",size=(5, 1)),sg.Text('chronology K (day)', size=(10, 2)), sg.InputText(initial_chron_k,key="chron_k",size=(5, 1))],
			[sg.Checkbox('Make item?', default=False,key='if_item',font = ('Helvetica', 15, 'bold italic'))],
			[sg.Text('Serial POL', size=(17, 1)), sg.InputText(initial_pol,key='serial_po_line',size=(35, 1))],
			[sg.Text('API_key (opt)', size=(17, 1)), sg.InputText(initial_api,key='api_key',size=(35, 1))],
			[sg.Checkbox('Add 942 field?', default=False,key='if_update',font = ('Helvetica', 15, 'bold italic'))],
			[sg.Text('942 statement',size=(17, 1)), sg.InputText(initial_942, key="field942",size=(35, 1))],
			[sg.Button("Run!")]

			]
	
	window =sg.Window(f'Podcasts GUI ("{r}" theme)', layout, default_element_size=(35, 2))#,background_color='#ACBAAB')
	event,values=window.read()

	return values,window,event



class PodcastTool():
	def __init__(self, api_key):
		self.api_key = api_key
		pass
	def add_942(self, mms_id ,record_xml, field942):
		record = parse_xml_to_array(io.StringIO(record_xml))[0]
		fields = record.get_fields('942')
		if len(fields) == 0:
			f942 = Field(tag = '942', indicators = ["",""], subfields = ['a', field942])
			record.add_ordered_field(f942)
			print(record)
			start_xml = r'<?xml version="1.0" encoding="UTF-8"?><bib><record_format>marc21</record_format><suppress_from_publishing>false</suppress_from_publishing><suppress_from_external_search>false</suppress_from_external_search><sync_with_oclc>BIBS</sync_with_oclc>'
			end_xml = '</bib>'
			bib_data =start_xml+str(record_to_xml(record)).replace("\\n", "\n").replace("\\", "")+end_xml
			print(bib_data)
			url = r"https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}".format(mms_id)
			parameters = {"apikey": self.api_key}
			r = requests.put(url, params = parameters,data=bib_data.encode("utf-8"),  headers=headers, verify= False)
			print(r.text)
			return r.status_code
		else:
			return None
		




	def parse_bib_record(self, record_xml):
		record = parse_xml_to_array(io.StringIO(record_xml))[0]
		year = record["264"]["c"].strip("[]()")
		return year

	def get_bib(self, mms_id):
		"""Retrieves bibliographic record record.
		Parameters:
			mms_id(str) - Alma bib record objectIdentifier
		Returns:
			r.text(str) - item_data in xml format
		"""
		url = r"https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}".format(mms_id)
		parameters = {"apikey": self.api_key}
		r = requests.get(url, params = parameters, verify= False)
		return r.text

	def get_item(self, mms_id, holding_id, item_pid):
		"""Retrieves item  record.
		Parameters:
			mms_id(str) - Alma bib record objectIdentifier
			holding_id(str) - holding id
			item_pid(str) - item pid
		Returns:
			r.text(str) - item_data in xml format
		"""
		print(self.api_key)
		url = r"https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/holdings/{}/items/{}".format(mms_id, holding_id, item_pid)
		parameters = {"apikey": self.api_key}
		r = requests.get(url, params = parameters, verify= False)
		return r.text

	def update_item(self, mms_id, holding_id, item_pid, item_data):
		"""Updates item with generating description
		Parameters:
			mms_id(str) - Alma bib record objectIdentifier
			holding_id(str) - holding id
			item_pid(str) - item pid
			item_data(str) - item data in xml format
		Returns:
			description(str) - description
			status_code(int) - response code - 200 if success, 404 if opposite

		"""

		url = r"https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/holdings/{}/items/{}".format(mms_id, holding_id, item_pid)
		parameters = {"apikey": self.api_key,"generate_description":True}
		r = requests.put(url, data = item_data.encode("utf-8"), headers=headers, params = parameters, verify= False)
		description= re.findall(r"<description>(.*?)</description>", r.text)[0]

		return description, r.status_code


	def get_serial_po_line(self,mms_id):
		"""Retrievs PO_line by mms_id"""
		# 		https://api-eu.hosted.exlibrisgroup.com/almaws/v1/acq/po-lines?q=mms_id~{mms_id}&status=ACTIVE&limit=100&offset=0&order_by=title&direction=desc&apikey={master.api_key}&expand=LOCATIONS
		url = r"https://api-ap.hosted.exlibrisgroup.com/almaws/v1/acq/po-lines"
		parameters = {"apikey": self.api_key,"q":"mms_id~{}".format(mms_id), "limit":"100", "order_by":"title"}
		r = requests.get(url, params = parameters, verify= False)
		print(r.text)
		print(r.url)
		quit()
		return r.text

	def get_holdings(self, mms_id):

		print("here1")
		url = r"https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/holdings".format(self.mms_id)
		params = {"apikey": self.api_key}
		r = requests.get(url, params = params,verify= False)
		try:

			holding_id= re.findall(r"<holding_id>(.*?)</holding_id>", r.text)[0]

			return holding_id
		except Exception as e:
			return None



	def create_holding(self, mms_id, xml_record_data):
		
		"""
		Creates item
		Parameters:
			mms_id(str) - Alma MMS ID
			xml_record_data - item xml
			options(dict) - optional parameters for request
		Returns:
			None
		"""
		print(self.api_key)
		xml_record_data = xml_record_data.replace("\\", "")
		parameters = {"apikey": self.api_key}
		print(parameters)
		r = requests.post("https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/holdings".format(mms_id), headers=headers, params=parameters, data=xml_record_data.encode("utf-8"),verify= False)
		try:
			holding_id= re.findall(r"<holding_id>(.*?)</holding_id>", r.text)[0]
			return holding_id
		except Exception as e:
			print(str(e))

			return None

	def create_item(self, mms_id, holding_id, xml_record_data):

		"""
		Creates item
		Parameters:
			mms_id(str) - Alma MMS ID
			holding_id(str) Alma holding ID
			xml_record_data - item xml
		Returns:
			None
		"""
		xml_record_data = xml_record_data.replace("\\", "")
		parameters = {"apikey": self.api_key,"generate_description":True}
		r = requests.post("https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/holdings/{}/items".format(mms_id, holding_id), headers=headers, params=parameters, data=xml_record_data.encode("utf-8"),verify= False)
		try:
			print(r.text)
			print(r.url)
			item_pid= re.findall(r"<pid>(.*?)</pid>", r.text)[0]
			return item_pid
		except Exception as e:
			print(str(e))
			return None



	def make_item(self, mms_id, serial_po_line, enum_a=None, enum_b=None, enum_c=None, chron_i=None, chron_j=None, chron_k=None):
		"""

		Main function for making Alma item record with existing template and parameters, writes down report and prints item_id
		Parameters:
			pub_name (str) - magazine name
			enum_a (str) - enumeration a
			enum_b (str) - enumeration b
			enum_c (str) - enumeration c
			chron_i (str) - chronology i
			chron_j (str) - chronology j
			chron_k (str) - chronology k
		Returns:
			None


		"""

		self.mms_id = mms_id
		self.serial_po_line = serial_po_line
		holding_id = self.get_holdings(mms_id)
		print(holding_id)
		if not holding_id:
			sg.Print("Making holding")
			holding_data = """
				<holding>
				<holding_id/>
				<suppress_from_publishing>false</suppress_from_publishing>
				<record>
				<leader>#####nu##a22#####1n#4500</leader>
				<controlfield tag="008">######0u####8###4001bueng0000000</controlfield>
				<datafield tag="852" ind1="8" ind2=" ">
				<subfield code="b">ATL</subfield>
				<subfield code="c">ATL.DA</subfield>
				</datafield>
				</record>
				</holding>
			"""
			holding_id = self.create_holding(mms_id, holding_data)
			sg.Print(holding_id)
		

		chron_i_stat = "<chronology_i></chronology_i>"
		chron_j_stat = "<chronology_j></chronology_j>"
		chron_k_stat = "<chronology_k></chronology_k>"
		enum_a_stat = "<enumeration_a></enumeration_a>"
		enum_b_stat = "<enumeration_b></enumeration_b>"
		enum_c_stat = "<enumeration_c></enumeration_c>"
		polstring = "<po_line>{}</po_line>".format(serial_po_line)

		if chron_i:
			chron_i_stat = "<chronology_i>{}</chronology_i>".format( chron_i )
		if chron_j:
			chron_j_stat = "<chronology_j>{}</chronology_j>".format( chron_j )
		if chron_k:
			chron_k_stat = "<chronology_k>{}</chronology_k>".format( chron_k )
		if enum_a:
			enum_a_stat = "<enumeration_a>{}</enumeration_a>".format( enum_a )
		if enum_b:
			enum_b_stat = "<enumeration_b>{}</enumeration_b>".format( enum_b)
		if  enum_c:
			enum_c_stat = "<enumeration_c>{}</enumeration_c>".format( enum_c)
		time_substitute_statement = "<creation_date>{}</creation_date>".format(str(dt.now().strftime( '%Y-%m-%d')))
		receiving_stat = "<arrival_date>{}</arrival_date>".format(str(dt.now().strftime( '%Y-%m-%d')))
		holding_stat = "<holding_id>{}</holding_id>".format(holding_id)
		item_data = """<item>
							  <holding_data>
							       <holding_id></holding_id>
							  </holding_data>
							  <item_data>
							    <pid></pid>
							    <creation_date></creation_date>
							    <physical_material_type desc="Digital File">KEYS</physical_material_type>
							    <policy>HERITAGE</policy>
							    <po_line></po_line>
							    <arrival_date></arrival_date>
							    <enumeration_a></enumeration_a>
							    <enumeration_b></enumeration_b>
							    <enumeration_c></enumeration_c>
								<chronology_i></chronology_i>
							    <chronology_j></chronology_j>
							    <chronology_k></chronology_k>
							    <receiving_operator>korotesv_API</receiving_operator>
								<library desc="Alexander Turnbull Library">ATL</library>
							    <location desc="Alexander Turnbull Library">ATL.DA</location>
							    <requested>false</requested>
							  </item_data>
							</item>
						"""
		print(item_data)
		item_data = item_data.replace("<creation_date></creation_date>", time_substitute_statement)
		item_data = item_data.replace("<po_line></po_line>", polstring )
		item_data = item_data.replace("<enumeration_a></enumeration_a>", enum_a_stat )
		item_data = item_data.replace("<enumeration_b></enumeration_b>", enum_b_stat )
		item_data = item_data.replace("<enumeration_c></enumeration_c>", enum_c_stat )
		item_data = item_data.replace("<chronology_i></chronology_i>", chron_i_stat )
		item_data = item_data.replace("<chronology_j></chronology_j>", chron_j_stat )
		item_data = item_data.replace("<chronology_k></chronology_k>", chron_k_stat )
		item_data = item_data.replace("<holding_id></holding_id>", holding_stat )

		sg.Print("Making item")
		item_pid = self.create_item(mms_id, holding_id,item_data)
		if item_pid:
			sg.Print("Item created ",item_pid)
		else:
			sg.Print("Could not create item")
		


# # Volume = dcterms:bibliographicCitation
# # Issue = dcterms:issued
# # Number = dcterms:accrualPeriodicity
# # Year = dc:date
# # Month = dcterms:available
# # Day = dc:coverage




	def make_SIP(self, podcast_name, episode_title, mms_id, policy="100", output_folder=None,  sip_output_folder =None, sip_detailed_output_folder = None,  enum_a=None, enum_b=None, enum_c=None, chron_i=None, chron_j=None, chron_k=None ):

			"""Method is used for making SIPs from description information

			Returns:
				bool  - True, if built, False otherwise
			"""
			self.output_folder= str(output_folder)
			self.sip_output_folder = str(sip_output_folder)
			sg.Print("Making sips")
			sg.Print(sip_output_folder)
			# try:
			build_sip(
									ie_dmd_dict=[{"dc:date":chron_i, "dcterms:available":chron_j, "dcterms:issued":enum_c, "dc:coverage":chron_k,"dcterms:bibliographicCitation":enum_a,  "dc:title":podcast_name,"dcterms:accrualPeriodicity":enum_b, "dcterms:bibliographicCitation":enum_a}],
									pres_master_dir=output_folder,
									generalIECharacteristics=[{"IEEntityType":"PeriodicIE","UserDefinedA":username}],
									objectIdentifier= [{"objectIdentifierType":"ALMAMMS", "objectIdentifierValue":mms_id}],
									accessRightsPolicy=[{"policyId":policy}],
									input_dir=output_folder,
									digital_original=True,
									output_dir=self.sip_output_folder,
									sip_title=sip_detailed_output_folder,
									# reduced_tags=True
								)
			sg.Print('Done in', sip_output_folder)
			# except Exception as e:
			# 	sg.Print(str(e))


	def download (self, my_link, output_folder):

		"""This function downloads ISSUU images from link"""
		sg.Print("Downloading...")
		r = requests.get(my_link,stream=True,verify= False)

		if str(r.status_code).startswith("2"):
			header_size = r.headers['Content-length']
			try:
				wget.download(my_link, out =output_folder)

			except urllib.error.HTTPError as e:
				print(str(e))
			except Exception as e:
				print(str(e))
		file_name = os.listdir(output_folder)[0]
		file_path = os.path.join(output_folder, file_name)
		size = os.path.getsize(file_path)
		if size!=0 and str(size)==str(header_size):
			sg.Print("File {} downloaded. Passed size check.".format(file_name))
		else:
			sg.Print("File {} size is  {} , should be {}.".format(filename, size))
		

def main():

	my_link = None
	sip_output_folder = None
	output_folder = None
	window = None
	

	values = None
	while True:
			try:
				if window:
					window.close()
				values,window,event= my_gui(values = values)
				print(values)
				if event == sg.WIN_CLOSED:
						break
				if event in (sg.WIN_CLOSED, 'Quit'):
					break
				pol_flag = False
				podcast_name = values["podc_name"].rstrip(" ")
				episode_title = values["ep_title"].rstrip(" ")
				mms_id = values["mms_id"].rstrip(" ")
				api_key = values["api_key"].rstrip(" ")
				serial_po_line = values["serial_po_line"].rstrip(" ")
				chron_i = values["chron_i"].rstrip(" ")
				chron_j = values["chron_j"].rstrip(" ")
				chron_k = values["chron_k"].rstrip(" ")
				enum_a = values["enum_a"].rstrip(" ")
				enum_b = values["enum_b"].rstrip(" ")
				enum_c = values["enum_c"].rstrip(" ")
				access =values['access'].rstrip(" ")
				url = values["url"].rstrip(" ")
				output_folder = values["output_folder"].rstrip(" ")
				sip_output_folder = values["output_sip_folder"].rstrip(" ")
				field942 = values["field942"]
				if_download = values["if_download"]
				if_sip = values["if_sip"]
				if_item = values["if_item"]
				if_update = values["if_update"]
				if not if_download and not if_sip and not if_item and not if_update:
					sg.Print("Please tick the option")
				elif if_download or if_sip or if_item or if_update:
					# if not title:
					# 	title = "Family care"
					# 	values["dc_title"] = str(title)
					if not mms_id or mms_id=="":
						mms_id ="9919009265602836"
					print(mms_id)


					# 	values["mms_id"] = str(mms_id)
					if not api_key or str(api_key)=="":
						api_key = str(apikey)

					# if not po_line:
					# 	po_line = "245690-ilsdb"
					# 	values["po_line"] = str(po_line)
					# if not url:
					# 	url = my_link
					# 	values["url"] = str(url)
					if not output_folder:
						output_folder = str(out_folder)
						values["output_folder"] = str(output_folder)
					if not sip_output_folder:
						sip_output_folder = str(sip_out_folder)
						values["output_sip_folder"] = str(sip_output_folder)
					if not os.path.isdir(output_folder):
						os.mkdir(output_folder)
					if not os.path.isdir(sip_output_folder):
						os.mkdir(sip_output_folder)
					if if_sip or if_item or if_update:
						pt = PodcastTool(api_key)
						podcast_xml = pt.get_bib(mms_id)
						if not chron_i:
							chron_i = pt.parse_bib_record(podcast_xml)

					if if_item:
						if not serial_po_line:
							try:
								print("here1")
								serial_po_line = podcasts_dict[podcast_name]["serial_pol"]
								print("here2")
								pol_flag = True
							except Exception as e:
								print(str(e))
								print("Could not find serial po_line. Please enter serial MMS id or serial PO_line and rerun the tool")
								sg.Print("Tool could not find PO-line for series. Please provide and try again.")
								
						else:
							pol_flag = True


					if not pol_flag and not if_item:
						pol_flag = True
					print(pol_flag)
					if pol_flag:
						sg.Print("Alma MMS: ", mms_id)
						sg.Print("Alma API key: ", api_key)
						sg.Print("Alma serial PO line: ", serial_po_line)
						sg.Print("Year: ", chron_i)

						
						if if_download:
							if len(os.listdir(output_folder))!=0:
								for fl in os.listdir(output_folder):
									os.remove(os.path.join(output_folder, fl))
							pt.download(url, output_folder)
						
						description = make_description(enum_a, enum_b, enum_c, chron_i, chron_j, chron_k)
						if description.startswith("(") and description.endswith(")"):
							description = description.lstrip("(").rstrip(")")
						sip_detailed_output_folder = ("Podcasts_"+podcast_name + " " +"_".join(episode_title.split(" ")[:3])+"_"+description).replace("(","").replace(")","").replace(" ","_").replace(",","").replace("\\","_").replace("/","_")
						if if_sip:
							print("here1")
							if os.path.isdir(sip_output_folder):
								print("here2")
								shutil.rmtree(sip_output_folder)
							print("here3")
							pt.make_SIP( podcast_name = podcast_name, episode_title = episode_title, output_folder= output_folder, sip_output_folder = sip_output_folder,sip_detailed_output_folder = sip_detailed_output_folder, mms_id=mms_id, policy=access, chron_i=chron_i,chron_j=chron_j, chron_k=chron_k, enum_a = enum_a, enum_b = enum_b,enum_c = enum_c)
						if if_item:
							pt.make_item( mms_id=mms_id, serial_po_line=serial_po_line,chron_i=chron_i, chron_j=chron_j, chron_k=chron_k, enum_a = enum_a, enum_b = enum_b,enum_c = enum_c)
						if if_update:
							sg.Print("Updating record with 942 field")
							status_code = pt.add_942(mms_id ,podcast_xml, field942)
							if str(status_code).startswith("2"):
								sg.Print("Record {} updated".format(mms_id))
							elif not status_code:
								sg.Print("Record {} has 942 field".format(mms_id))
							else:
								sg.Print("Could not update record")
			except Exception as e:
				sg.Print(str(e))
				window.close()
	window.close()




if __name__ == "__main__":			
	main()
