import requests
from time import sleep
try:
	from settings import sb_key, pr_key
except:
	from settings_prod import sb_key, pr_key
from bs4 import BeautifulSoup as bs
import re
##################################################################################################
class AlmaTools():
	
	""" 
	This class contains methods for getting, updating, creating and deleting Alma data via Alma's APIs.

	Attributes
	----------
	mms_id : str
		Alma MMS IDF
	holding_id: str
		Alma holding ID
	item_pid : str
		Alma item ID
	xml_record_data : str
		XML data to submit to Alma
	options : dict
		dictionary which contains any API request parameters additional to the necessary API key. Example: "{"limit":"100"}"
	status_code : int
		status code for the Alma request
	xml_response_data:
		response in xml format

	Methods
	-------
		__init__(self, key)
		get_bib(self, mms_id, options)
		update_bib(self, mms_id, xml_record_data, options)
		get_holdings(self, mms_id, options)
		get_holding(self, mms_id, holding_id, options)
		delete_holding(self, mms_id, holding_id)
		get_items(self, mms_id, holding_id, options)
		get_item(self, mms_id, holding_id, item_pid, options)
		update_item(self, mms_id, holding_id, item_pid, xml_record_data, options)
		delete_item(self, mms_id, holding_id, item_pid)
		get_representations(self, mms_id, options)
		get_representation(self, mms_id, rep_id, options)
		update_representation(self, mms_id, rep_id, xml_record_data, options)
		create_item_by_po_line(self, po_line, xml_record_data, options)
		get_portfolio(self, mms_id, portfolio_id, options)
		delete_portfolio(self, mms_id, portfolio_id, options)
		get_ecollection(self, mms_id, ecollection_id, oprions)

	"""

	def __init__(self, alma_key):
		
		"""	Initialises all the neccessary attributes for an Alma_tools object.
			
			Parameters:
			alma_key (str) - Code for appropriate Alma API key - "sb" for sandbox or "prod" for production
		"""
		if alma_key == "sb":
			self.alma_key = str(sb_key)
		elif alma_key == "prod":
			self.alma_key = str(pr_key)
		self.base_api_url = "https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/"
		self.acq_base_api_url = "https://api-ap.hosted.exlibrisgroup.com/almaws/v1/acq/po-lines/"
		self.mms_id = None
		self.holding_id = None
		self.item_pid = None
		self.xml_response_data = None
		self.status_code = None
		self.headers = {'content-type': 'application/xml'}
		
	def get_bib(self, mms_id, options={}):

		""" Retrieves the bibliographic record in XML for a given Alma MMS ID
		Parameters:
			mms_id(str) - Alma MMS ID
			options(dict) - optional parameters for request
		Returns:
			self.xml_response_data
			self.status_code
		"""
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.get(f"{self.base_api_url}{mms_id}", params=parameters)
		self.xml_response_data = r.text
		self.status_code = r.status_code

	def get_ecollection(self, mms_id, ecollection_id, options = {}):

		"""
		Retrieves an electronic collection record in xml 
		Argumets:
			collection_id(str) - id of the collection
		"""

		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.get(f"{self.base_api_url}{mms_id}/e-collections/{ecollection_id}", params=parameters)
		print(r.text)
		self.xml_response_data = r.text
		self.status_code = r.status_code

	def get_portfolio(self, mms_id, portfolio_id, options = {}):

		"""
		Retrieves a portfolio record in xml 
		Argumets:
			mms_id(str) - id of the bibliographic record
			portfolio_id(str) - id of the portfolio
		"""

		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.get(f"{self.base_api_url}{mms_id}/portfolios/{portfolio_id}", params=parameters)
		self.xml_response_data = r.text
		self.status_code = r.status_code

	def delete_portfolio(self, mms_id, portfolio_id, options = {}):

		"""
		Deletes portfolio
		Argumets:
			mms_id(str) - id of the bibliographic record
			portfolio_id(str) - id of the portfolio
		Returns:
			None
		"""
		
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.delete (f"{self.base_api_url}{mms_id}/portfolios/{portfolio_id}", params=parameters)
		self.xml_response_data = r.text
		self.status_code = r.status_code



	def create_bib(self, xml_record_data, options = {}):

		"""
		Creates bibliographic record
		Paramrters:			
			xml_record_data(str) - xml of updated bib record data
			options(dict) - optional parameters for request
		Returns:
			self.xml_response_data
		"""
		
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.post(f"{self.base_api_url}", headers=self.headers, params=parameters, data=xml_record_data.encode("utf-8"))
		self.xml_response_data = r.text
		self.status_code = r.status_code

	def delete_bib(self, mms_id,options = {}):

		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.delete(f"{self.base_api_url}{mms_id}", params=parameters)
		self.xml_response_data = r.text
		self.status_code = r.status_code

	def update_bib(self, mms_id, xml_record_data, options={}):

		"""
		Updates bibliographic record.
		Parameters:
			mms_id(str) - Alma MMS ID
			xml_record_data(str) - xml of updated bib record data
			options(dict) - optional parameters for request
		Returns:
			self.xml_response_data
			self.status_code
		"""
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.put(f"{self.base_api_url}{mms_id}", headers=self.headers, params=parameters, data=xml_record_data.encode("utf-8"))
		self.xml_response_data=  r.text
		self.status_code = r.status_code

	def get_holdings(self, mms_id, options={}):

		"""
		Retrieves all holdings attached to a given MMS ID
		Parameters:
			mms_id(str) - Alma MMS ID
			options(dict) - optional parameters for request
		Returns:
			self.xml_response_data
			self.status_code
		"""
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.get(f"{self.base_api_url}{mms_id}/holdings", params=parameters)
		self.xml_response_data = r.text
		self.status_code = r.status_code

	def get_holding(self, mms_id, holding_id, options={}):

		"""
		Retrieves an individual holding by holding ID
		Parameters:
			mms_id(str) - Alma MMS ID
			holding_id(str) - Alma holding ID
			options(dict) - optional parameters for request
		Returns:
			self.xml_response_data
			self.status_code
		"""
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.get(f"{self.base_api_url}{mms_id}/holdings{holding_id}", params=parameters)
		self.xml_response_data = r.text
		self.status_code = r.status_code

	def create_holding(self, mms_id, xml_record_data, options={}):

		"""
		Creates item
		Parameters:
			mms_id(str) - Alma MMS ID
			holding_id(str) Alma holding ID
			xml_record_data - item xml
			options(dict) - optional parameters for request
		Returns:
			self.xml_response_data
			self.status_code
		"""
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.post(f"{self.base_api_url}{mms_id}/holdings", headers=self.headers, params=parameters, data=xml_record_data.encode("utf-8"))
		self.xml_response_data = r.text
		self.status_code = r.status_code

	def delete_holding(self, mms_id, holding_id):

		"""
		Deletes a holding by holding ID
		Parameters:
			mms_id(str) - Alma MMS ID
			holding_id(str) - Alma holding ID
		Returns:
			self.xml_response_data
			self.status_code
		"""
		r = requests.delete(f"{self.base_api_url}{mms_id}/holdings/{holding_id}?apikey={self.alma_key}")
		self.xml_response_data = r.text
		self.status_code = r.status_code
	
	def get_items(self, mms_id,  holding_id, options={}):

		"""
		Retrieves all items for MMS ID and holding ID
		Parameters:
			mms_id(str) - Alma MMS ID
			holding_id(str) - Alma holding ID
			options(dict) - optional parameters for request
		Returns:
			self.xml_response_data
			self.status_code
		"""
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.get(f"{self.base_api_url}{mms_id}/holdings/{holding_id}/items", params=parameters)
		self.xml_response_data = r.text
		self.status_code = r.status_code

	def get_item(self, mms_id, holding_id, item_pid, options={}):

		"""
		Retrieves an individual item by item PID
		Parameters:
			mms_id(str) - Alma MMS ID
			holding_id(str) Alma holding ID
			item_pid(str) - Alma item PID
			options(dict) - optional parameters for request
		Returns:
			self.xml_response_data
			self.status_code
		"""
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.get(f"{self.base_api_url}{mms_id}/holdings/{holding_id}/items/{item_pid}", params=parameters)
		self.xml_response_data = r.text
		self.status_code = r.status_code

	def create_item(self, mms_id, holding_id, xml_record_data, options={}):

		"""
		Creates item
		Parameters:
			mms_id(str) - Alma MMS ID
			holding_id(str) Alma holding ID
			xml_record_data - item xml
			options(dict) - optional parameters for request
		Returns:
			self.xml_response_data
			self.status_code
		"""
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.post(f"{self.base_api_url}{mms_id}/holdings/{holding_id}/items", headers=self.headers, params=parameters, data=xml_record_data.encode("utf-8"))
		self.xml_response_data = r.text
		self.status_code = r.status_code

	def update_item(self, mms_id, holding_id, item_pid, xml_record_data, options={}):
		
		"""
		Updates item with new item XML data

		Parameters:
			mms_id(str) - Alma MMS ID
			xml_record_data(str) - XML of updated item record data
			options(dict) - optional parameters for request
		Returns:
			self.xml_response_data
			self.status_code
		"""
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.put(f"{self.base_api_url}{mms_id}/holdings/{holding_id}/items/{item_pid}", headers=self.headers, params=parameters, data=xml_record_data.encode("utf-8"))
		self.xml_response_data=  r.text
		self.status_code = r.status_code

	def delete_item( self, mms_id, holding_id, item_pid):

		"""
		Deletes item by item PID
		Parameters:
			mms_id(str) - Alma MMS ID
			holding_id(str) Alma holding ID
			item_pid(str) - Alma item PID
		Returns:
			self.xml_response_data
			self.status_code
		"""
		r = requests.delete(f"{self.base_api_url}{mms_id}/holdings/{holding_id}/items/{item_pid}?apikey={self.alma_key}")
		self.xml_response_data = r.text
		self.status_code = r.status_code

	def get_representations(self, mms_id, options={}):

		"""
		Retrieves digital representations attached to a given MMS ID 
		Parameters:
			mms_id(str) - Alma MMS ID
			options(dict) - optional parameters for request
		Returns:
			None
		"""
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.get(f"{self.base_api_url}{mms_id}/representations", params=parameters)
		self.xml_response_data=  r.text
		self.status_code = r.status_code
	def get_representation(self, mms_id, rep_id, options={}):

		"""
		Retrieves digital representations attached to a given MMS ID 
		Parameters:
			mms_id(str) - Alma MMS ID
			options(dict) - optional parameters for request
			rep_id(str) - Alma representation id
		Returns:
			None
		"""
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.get(f"{self.base_api_url}{mms_id}/representations/{rep_id}", params=parameters)
		self.xml_response_data=  r.text
		self.status_code = r.status_code

	def update_representation(self, mms_id, rep_id, xml_record_data, options={}):

		"""
		Updates represeintation with new digital represeintation XML data

		Parameters:
			mms_id(str) - Alma MMS ID
			rep_id(str) - Alma representation id
			xml_record_data(str) - XML of updated item record data
			options(dict) - optional parameters for request
		Returns:
			self.xml_response_data
			self.status_code
		"""
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.put(f"{self.base_api_url}{mms_id}/representations/{rep_id}", headers=self.headers, params=parameters, data=xml_record_data.encode("utf-8"))
		self.xml_response_data=  r.text
		self.status_code = r.status_code



	def get_po_line(self, po_line, options={}):

		""" 
		Retrieves the purchase order line  in XML for a given Alma POL
		Parameters:
			po_line(str) - Alma POL
			options(dict) - optional parameters for request
		Returns:
			self.xml_response_data
			self.status_code
		"""
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.get(f"{self.acq_base_api_url}{po_line}", params=parameters)
		self.xml_response_data = r.text
		self.status_code = r.status_code

	def update_po_line(self, po_line, xml_record_data, options={}):

		"""
		Updates POL.
		Parameters:
			po_line(str) - Alma POL
			xml_record_data(str) - xml of updated POL 
			options(dict) - optional parameters for request
		Returns:
			self.xml_response_data
			self.status_code
		"""
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.put(f"{self.acq_base_api_url}{po_line}", headers=self.headers, params=parameters, data=xml_record_data.encode("utf-8"))
		self.xml_response_data=  r.text
		self.status_code = r.status_code


	def create_item_by_po_line(self, po_line, xml_record_data, options={}):

		"""
		Creates item.
		Parameters:
			po_line(str) - Alma POL
			xml_record_data(str) - new item in xml format
			options(dict) - optional parameters for request
		Returns:
			self.xml_response_data
			self.status_code
		Notes:
			holding_id required in the  xml data
		"""

		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.post(f"{self.acq_base_api_url}{po_line}/items", headers=self.headers, params=parameters, data=xml_record_data.encode("utf-8"))
		self.xml_response_data = r.text
		self.status_code = r.status_code



def main():

	"""Example of usage"""

	#mms_id = "9918975967302836"

	my_api = AlmaTools("prod")
	# mis_mms_list = ['9919046572802836','9919046573002836']
	# for mms in mis_mms_list:
	# 		my_api.delete_bib(mms)
	# 		print(my_api.xml_response_data.encode("utf-8"))
	#######################################
	# my_api.get_bib(mms_id, {"limit":"100"})
	# print(my_api.xml_response_data.encode("utf-8"))
	# #######################################
	# my_api.get_holdings(mms_id, {"limit":"100"})
	# print(my_api.xml_response_data.encode("utf-8"))
	#######################################
	# my_api.update_bib(mms_id, my_api.xml_record_data)
	# print(my_api.status_code)
	#######################################
	# my_api.get_representations(mms_id)
	# print(my_api.xml_response_data.encode("utf-8"))
	###############################################
	# my_api.get_porfolio("9919012972402836","53354322810002836")
	# print(my_api.xml_response_data)
	# print(my_api.status_code)
	#########################################
	# my_api.get_ecollection("9918748064302836","61325625670002836")
	# print(my_api.xml_response_data)
	# print(my_api.status_code)
	# ####################################################################
	# my_api.get_po_line("POL-32856")
	# print(my_api.xml_response_data)
	# print(my_api.status_code)
	####################################################################
	# my_api.get_item("9918166772702836","22294172070002836","23361571080002836")
	# print(my_api.xml_response_data)
	# print(my_api.status_code)
	# ####################################################################
	# my_api.get_po_line("POL-32856")
	# print(my_api.xml_response_data)
	# print(my_api.status_code)
	####################################################################
	# my_list = [["9918166769702836","22294170890002836","23361559820002836"],["9918166769702836","22294170890002836","23361570070002836"],["9918166772702836","22294172070002836","23361571080002836"],["9918166769902836","22294170920002836","23361571070002836"],["9918166769502836","22294170850002836","23361559680002836"],["9918963672702836","22346162470002836","23361559670002836"],["9918166769602836","22294170870002836","23361571060002836"],["9916482513502836","22218301930002836","23361559620002836"],["9918166770602836","22294170970002836","23361557880002836"],["9918166772902836","22294172110002836","23361559600002836"],["9913788543502836","22194217920002836","23361571050002836"]]
	# for lst in my_list:
	# 	mms_id= lst[0]
	# 	holding_id = lst[1]
	# 	item_pid = lst[2]
	# 	my_api.delete_item(mms_id, holding_id, item_pid)
	# 	print(my_api.xml_response_data)
	##################################################################################
	# file_path = r"mms_to_delete.txt"
	# with open(file_path,"r") as f:
	# 	data = f.read()
	# for el in data.split("\n"):
	# 	my_api.delete_bib(el)
	#################################################################################
	# mms_list = []
	# for mms in mms_list:
	# 	my_api.delete_bib(mms)
	#####################UPDATE REPRESENTATION########################################3
# 	my_xml_dict = {
# 	'32361841600002836':'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><representations><representation> is_remote="true" link="https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/9913231823502836/representations/32361841600002836"><id>32361841600002836</id><library desc="The Alexander Turnbull Library">ATL</library><label>iss.01APR21 2021 04 01 </label><public_note>Limited On Site Access</public_note><usage_type desc="Master">PRESERVATION_MASTER</usage_type><active desc="Active">true</active><entity_type desc="Issue-Detailed">IssueDet</entity_type><issue>01APR21</issue><year>2021</year><season_month>04</season_month><day_in_month>01</day_in_month><delivery_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66796195</delivery_url><thumbnail_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66796195&amp;dps_func=thumbnail</thumbnail_url><repository desc="National Digital Heritage Archive">NDHA_PROD-OAIDC01</repository><originating_record_id>oai:d4I1-pubam:IE66796195</originating_record_id><linking_parameter_1>IE66796195</linking_parameter_1><linking_parameter_2></linking_parameter_2><linking_parameter_3></linking_parameter_3><linking_parameter_4></linking_parameter_4><linking_parameter_5></linking_parameter_5><created_by>exl_api</created_by><created_date>2021-04-20Z</created_date><last_modified_by>exl_api</last_modified_by><last_modified_date>2021-04-20Z</last_modified_date></representation></representations>',
# '32361830170002836':'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><representations><representation> is_remote="true" link="https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/9913231823502836/representations/32361830170002836"><id>32361830170002836</id><library desc="The Alexander Turnbull Library">ATL</library><label>iss.06APR21 2021 04 06 </label><public_note>Limited On Site Access</public_note><usage_type desc="Master">PRESERVATION_MASTER</usage_type><active desc="Active">true</active><entity_type desc="Issue-Detailed">IssueDet</entity_type><issue>06APR21</issue><year>2021</year><season_month>04</season_month><day_in_month>06</day_in_month><delivery_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66795725</delivery_url><thumbnail_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66795725&amp;dps_func=thumbnail</thumbnail_url><repository desc="National Digital Heritage Archive">NDHA_PROD-OAIDC01</repository><originating_record_id>oai:d4I1-pubam:IE66795725</originating_record_id><linking_parameter_1>IE66795725</linking_parameter_1><linking_parameter_2></linking_parameter_2><linking_parameter_3></linking_parameter_3><linking_parameter_4></linking_parameter_4><linking_parameter_5></linking_parameter_5><created_by>exl_api</created_by><created_date>2021-04-20Z</created_date><last_modified_by>exl_api</last_modified_by><last_modified_date>2021-04-20Z</last_modified_date></representation></representations>',
# '32361830190002836':'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><representations><representation> is_remote="true" link="https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/9913231823502836/representations/32361830190002836"><id>32361830190002836</id><library desc="The Alexander Turnbull Library">ATL</library><label>iss.12APR21 2021 04 12 </label><public_note>Limited On Site Access</public_note><usage_type desc="Master">PRESERVATION_MASTER</usage_type><active desc="Active">true</active><entity_type desc="Issue-Detailed">IssueDet</entity_type><issue>12APR21</issue><year>2021</year><season_month>04</season_month><day_in_month>12</day_in_month><delivery_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66795691</delivery_url><thumbnail_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66795691&amp;dps_func=thumbnail</thumbnail_url><repository desc="National Digital Heritage Archive">NDHA_PROD-OAIDC01</repository><originating_record_id>oai:d4I1-pubam:IE66795691</originating_record_id><linking_parameter_1>IE66795691</linking_parameter_1><linking_parameter_2></linking_parameter_2><linking_parameter_3></linking_parameter_3><linking_parameter_4></linking_parameter_4><linking_parameter_5></linking_parameter_5><created_by>exl_api</created_by><created_date>2021-04-20Z</created_date><last_modified_by>exl_api</last_modified_by><last_modified_date>2021-04-20Z</last_modified_date></representation></representations>',
# '32362169660002836':'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><representations><representation> is_remote="true" link="https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/9913231823502836/representations/32362169660002836"><id>32362169660002836</id><library desc="The Alexander Turnbull Library">ATL</library><label>iss.29APR21 2021 04 29 </label><public_note>Limited On Site Access</public_note><usage_type desc="Master">PRESERVATION_MASTER</usage_type><active desc="Active">true</active><entity_type desc="Issue-Detailed">IssueDet</entity_type><issue>29APR21</issue><year>2021</year><season_month>04</season_month><day_in_month>29</day_in_month><delivery_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE67700992</delivery_url><thumbnail_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE67700992&amp;dps_func=thumbnail</thumbnail_url><repository desc="National Digital Heritage Archive">NDHA_PROD-OAIDC01</repository><originating_record_id>oai:d4I1-pubam:IE67700992</originating_record_id><linking_parameter_1>IE67700992</linking_parameter_1><linking_parameter_2></linking_parameter_2><linking_parameter_3></linking_parameter_3><linking_parameter_4></linking_parameter_4><linking_parameter_5></linking_parameter_5><created_by>exl_api</created_by><created_date>2021-05-04Z</created_date><last_modified_by>exl_api</last_modified_by><last_modified_date>2021-05-04Z</last_modified_date></representation></representations>',
# '32362019360002836':'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><representations><representation> is_remote="true" link="https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/9913231823502836/representations/32362019360002836"><id>32362019360002836</id><library desc="The Alexander Turnbull Library">ATL</library><label>iss.22APR21 2021 04 22 </label><public_note>Limited On Site Access</public_note><usage_type desc="Master">PRESERVATION_MASTER</usage_type><active desc="Active">true</active><entity_type desc="Issue-Detailed">IssueDet</entity_type><issue>22APR21</issue><year>2021</year><season_month>04</season_month><day_in_month>22</day_in_month><delivery_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE67554477</delivery_url><thumbnail_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE67554477&amp;dps_func=thumbnail</thumbnail_url><repository desc="National Digital Heritage Archive">NDHA_PROD-OAIDC01</repository><originating_record_id>oai:d4I1-pubam:IE67554477</originating_record_id><linking_parameter_1>IE67554477</linking_parameter_1><linking_parameter_2></linking_parameter_2><linking_parameter_3></linking_parameter_3><linking_parameter_4></linking_parameter_4><linking_parameter_5></linking_parameter_5><created_by>exl_api</created_by><created_date>2021-04-29Z</created_date><last_modified_by>exl_api</last_modified_by><last_modified_date>2021-04-29Z</last_modified_date></representation></representations>',
# '32362149710002836':'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><representations><representation> is_remote="true" link="https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/9913231823502836/representations/32362149710002836"><id>32362149710002836</id><library desc="The Alexander Turnbull Library">ATL</library><label>iss.28APR21 2021 04 28 </label><public_note>Limited On Site Access</public_note><usage_type desc="Master">PRESERVATION_MASTER</usage_type><active desc="Active">true</active><entity_type desc="Issue-Detailed">IssueDet</entity_type><issue>28APR21</issue><year>2021</year><season_month>04</season_month><day_in_month>28</day_in_month><delivery_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE67700966</delivery_url><thumbnail_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE67700966&amp;dps_func=thumbnail</thumbnail_url><repository desc="National Digital Heritage Archive">NDHA_PROD-OAIDC01</repository><originating_record_id>oai:d4I1-pubam:IE67700966</originating_record_id><linking_parameter_1>IE67700966</linking_parameter_1><linking_parameter_2></linking_parameter_2><linking_parameter_3></linking_parameter_3><linking_parameter_4></linking_parameter_4><linking_parameter_5></linking_parameter_5><created_by>exl_api</created_by><created_date>2021-05-04Z</created_date><last_modified_by>exl_api</last_modified_by><last_modified_date>2021-05-04Z</last_modified_date></representation></representations>',
# '32361830070002836':'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><representations><representation> is_remote="true" link="https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/9913231823502836/representations/32361830070002836"><id>32361830070002836</id><library desc="The Alexander Turnbull Library">ATL</library><label>iss.08APR21 2021 04 08 </label><public_note>Limited On Site Access</public_note><usage_type desc="Master">PRESERVATION_MASTER</usage_type><active desc="Active">true</active><entity_type desc="Issue-Detailed">IssueDet</entity_type><issue>08APR21</issue><year>2021</year><season_month>04</season_month><day_in_month>08</day_in_month><delivery_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66795923</delivery_url><thumbnail_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66795923&amp;dps_func=thumbnail</thumbnail_url><repository desc="National Digital Heritage Archive">NDHA_PROD-OAIDC01</repository><originating_record_id>oai:d4I1-pubam:IE66795923</originating_record_id><linking_parameter_1>IE66795923</linking_parameter_1><linking_parameter_2></linking_parameter_2><linking_parameter_3></linking_parameter_3><linking_parameter_4></linking_parameter_4><linking_parameter_5></linking_parameter_5><created_by>exl_api</created_by><created_date>2021-04-20Z</created_date><last_modified_by>exl_api</last_modified_by><last_modified_date>2021-04-20Z</last_modified_date></representation></representations>',
# '32361841740002836':'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><representations><representation> is_remote="true" link="https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/9913231823502836/representations/32361841740002836"><id>32361841740002836</id><library desc="The Alexander Turnbull Library">ATL</library><label>iss.07APR21 2021 04 07 </label><public_note>Limited On Site Access</public_note><usage_type desc="Master">PRESERVATION_MASTER</usage_type><active desc="Active">true</active><entity_type desc="Issue-Detailed">IssueDet</entity_type><issue>07APR21</issue><year>2021</year><season_month>04</season_month><day_in_month>07</day_in_month><delivery_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66795757</delivery_url><thumbnail_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66795757&amp;dps_func=thumbnail</thumbnail_url><repository desc="National Digital Heritage Archive">NDHA_PROD-OAIDC01</repository><originating_record_id>oai:d4I1-pubam:IE66795757</originating_record_id><linking_parameter_1>IE66795757</linking_parameter_1><linking_parameter_2></linking_parameter_2><linking_parameter_3></linking_parameter_3><linking_parameter_4></linking_parameter_4><linking_parameter_5></linking_parameter_5><created_by>exl_api</created_by><created_date>2021-04-20Z</created_date><last_modified_by>exl_api</last_modified_by><last_modified_date>2021-04-20Z</last_modified_date></representation></representations>',
# '32361841560002836':'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><representations><representation> is_remote="true" link="https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/9913231823502836/representations/32361841560002836"><id>32361841560002836</id><library desc="The Alexander Turnbull Library">ATL</library><label>iss.15APR21 2021 04 15 </label><public_note>Limited On Site Access</public_note><usage_type desc="Master">PRESERVATION_MASTER</usage_type><active desc="Active">true</active><entity_type desc="Issue-Detailed">IssueDet</entity_type><issue>15APR21</issue><year>2021</year><season_month>04</season_month><day_in_month>15</day_in_month><delivery_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66796370</delivery_url><thumbnail_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66796370&amp;dps_func=thumbnail</thumbnail_url><repository desc="National Digital Heritage Archive">NDHA_PROD-OAIDC01</repository><originating_record_id>oai:d4I1-pubam:IE66796370</originating_record_id><linking_parameter_1>IE66796370</linking_parameter_1><linking_parameter_2></linking_parameter_2><linking_parameter_3></linking_parameter_3><linking_parameter_4></linking_parameter_4><linking_parameter_5></linking_parameter_5><created_by>exl_api</created_by><created_date>2021-04-20Z</created_date><last_modified_by>exl_api</last_modified_by><last_modified_date>2021-04-20Z</last_modified_date></representation></representations>',
# '32361997560002836':'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><representations><representation> is_remote="true" link="https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/9913231823502836/representations/32361997560002836"><id>32361997560002836</id><library desc="The Alexander Turnbull Library">ATL</library><label>iss.27APR21 2021 04 27 </label><public_note>Limited On Site Access</public_note><usage_type desc="Master">PRESERVATION_MASTER</usage_type><active desc="Active">true</active><entity_type desc="Issue-Detailed">IssueDet</entity_type><issue>27APR21</issue><year>2021</year><season_month>04</season_month><day_in_month>27</day_in_month><delivery_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE67554376</delivery_url><thumbnail_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE67554376&amp;dps_func=thumbnail</thumbnail_url><repository desc="National Digital Heritage Archive">NDHA_PROD-OAIDC01</repository><originating_record_id>oai:d4I1-pubam:IE67554376</originating_record_id><linking_parameter_1>IE67554376</linking_parameter_1><linking_parameter_2></linking_parameter_2><linking_parameter_3></linking_parameter_3><linking_parameter_4></linking_parameter_4><linking_parameter_5></linking_parameter_5><created_by>exl_api</created_by><created_date>2021-04-29Z</created_date><last_modified_by>exl_api</last_modified_by><last_modified_date>2021-04-29Z</last_modified_date></representation></representations>',
# '32361829930002836':'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><representations><representation> is_remote="true" link="https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/9913231823502836/representations/32361829930002836"><id>32361829930002836</id><library desc="The Alexander Turnbull Library">ATL</library><label>iss.09APR21 2021 04 09 </label><public_note>Limited On Site Access</public_note><usage_type desc="Master">PRESERVATION_MASTER</usage_type><active desc="Active">true</active><entity_type desc="Issue-Detailed">IssueDet</entity_type><issue>09APR21</issue><year>2021</year><season_month>04</season_month><day_in_month>09</day_in_month><delivery_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66796371</delivery_url><thumbnail_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66796371&amp;dps_func=thumbnail</thumbnail_url><repository desc="National Digital Heritage Archive">NDHA_PROD-OAIDC01</repository><originating_record_id>oai:d4I1-pubam:IE66796371</originating_record_id><linking_parameter_1>IE66796371</linking_parameter_1><linking_parameter_2></linking_parameter_2><linking_parameter_3></linking_parameter_3><linking_parameter_4></linking_parameter_4><linking_parameter_5></linking_parameter_5><created_by>exl_api</created_by><created_date>2021-04-20Z</created_date><last_modified_by>exl_api</last_modified_by><last_modified_date>2021-04-20Z</last_modified_date></representation></representations>',
# '32361829950002836':'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><representations><representation> is_remote="true" link="https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/9913231823502836/representations/32361829950002836"><id>32361829950002836</id><library desc="The Alexander Turnbull Library">ATL</library><label>iss.13APR21 2021 04 13 </label><public_note>Limited On Site Access</public_note><usage_type desc="Master">PRESERVATION_MASTER</usage_type><active desc="Active">true</active><entity_type desc="Issue-Detailed">IssueDet</entity_type><issue>13APR21</issue><year>2021</year><season_month>04</season_month><day_in_month>13</day_in_month><delivery_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66796352</delivery_url><thumbnail_url>https://ndhadeliver.natlib.govt.nz/delivery/DeliveryManagerServlet?dps_pid=IE66796352&amp;dps_func=thumbnail</thumbnail_url><repository desc="National Digital Heritage Archive">NDHA_PROD-OAIDC01</repository><originating_record_id>oai:d4I1-pubam:IE66796352</originating_record_id><linking_parameter_1>IE66796352</linking_parameter_1><linking_parameter_2></linking_parameter_2><linking_parameter_3></linking_parameter_3><linking_parameter_4></linking_parameter_4><linking_parameter_5></linking_parameter_5><created_by>exl_api</created_by><created_date>2021-04-20Z</created_date><last_modified_by>exl_api</last_modified_by><last_modified_date>2021-04-20Z</last_modified_date></representation></representations>',

# 	}
# 	replacement = [4435,4436,4440,4452,4448,4451,4438,4437,4443,4450,4439,4441]
# 	#missing=[4442,4444,4445,4446,4447,4449]
# 	count = 0
# 	for el in my_xml_dict.keys():
# 		xml = my_xml_dict[el]
# 		link = re.findall(r'link="(.*?)"',xml)[0]
# 		mms = re.findall(r'bibs/(.*?)/',link)[0]
# 		repres = link.split('/')[-1]
# 		my_api.get_representation(mms, repres)
# 		alma_xml = my_api.xml_response_data
# 		issue = re.findall(r'issue>(.*?)</issue',alma_xml)[0]
# 		new_alma_xml = alma_xml.replace(issue,str(replacement[count]))
# 		my_api.update_representation(mms, repres, new_alma_xml)
# 		count+=1



if __name__ == '__main__':
	main()