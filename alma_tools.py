import requests
from settings import sb_key, pr_key
from find_ie import getting_reps


##################################################################################################
class AlmaTools():
	
	""" 
	This class contains methods for getting, updating and deleting Alma data via Alma's APIs.

	Attributes
	----------
	mms_id : str
		Alma MMS ID
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

	"""

	def __init__(self, alma_key):
		
		"""	Initialises all the neccessary attributes for an Alma_tools object.
			
			Parameters:
			alma_key (str) - Code for appropriate Alma API key - "sb" for sandbox or "prod" for production
		"""
		if key == "sb":
		  self.alma_key = str(sb_key)
		elif key == "prod":
			self.alma_key = str(pr_key)
		self.base_api_url = "https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/"
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

	def create_bib(self, xml_record_datam, options = {}):

		"""
		Creates bibliographic record
		Paramrters:			
			xml_record_data(str) - xml of updated bib record data
			options(dict) - optional parameters for request
		Returns:
			self.xml_response_data
		"""
		
		parameters = {**{"apikey": self.alma_key}, **options}
		r = requests.put(f"{self.base_api_url}", headers=self.headers, params=parameters, data=xml_record_data.encode("utf-8"))
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
	

def main():

	"""Example of usage"""

	mms_id = "9918975967302836"

	my_api = Alma_tools(sb_key)

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


if __name__ == '__main__':
	main()