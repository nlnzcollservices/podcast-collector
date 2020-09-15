import requests
from settings import  sb_key, pr_key
from find_ie import getting_reps


##################################################################################################
class Alma_tools():
	
	""" 
		Alma_tools - a class which contains Alma APIs

		Attributes
		----------
		mms : str
			Alma mms id
		holding: str
			Alma holding id
		item : str
			Alma item id
		xml : str
			xml data to submit to Alma
		options : dict
			dictionary which contain API request options listed in url after API key and connected by '&'
		status_code : int
			status code for the Alma request

		Methods
		-------
			__init__(self, key)
			get_bib(self, mms, options)
			update_bib(self, mms, xml, options)
			get_holdings(self, mms, options )
			get_holding(self, mms, holding, options)
			get_items(self, mms,  holding, options)
			get_item(self, mms, holding, item, options)
			delete_item( self, mms, holding, item)
			delete_holding ( self, mms, holding)
			update_item (self, mms, holding, item, options)
			get (reps)

	"""

	def __init__(self, key):
		
		"""	Constructs all  the neccessary attributes for Alma_tools
			
			Parameters:
				key (str) - Alma API key could be for Production or for a Sandbox
		"""
		if key == "sb":
			self.alma_key = str(sb_key)
		elif key == "prod":
			self.alma_key = str(pr_key)
		self.status_code = None
		self.xml_data = None
		self.mms = None
		self.holding = None
		self.item = None 
		
	def get_bib( self, mms, options ):

		""" Retrieves bibliographic record xml
		Parameters:
			mms(str) - alma mms id
			options(dict) - options for request
		Returns:
			None
		"""
		url = 'https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}?apikey={}'.format( mms, self.alma_key)
		if options:
			option_string = ""
			for key in options.keys():
				url = url + "&"
				url = url + key + "=" + options[key]
		r = requests.get( url)
		self.xml_data=  r.text
		self.status_code = r.status_code

	def update_bib(self, mms, xml, options):

		"""
		Updates bibliographic record.
		Parameters:
			mms(str) - alma mms id
			xml(str) - xml for alma bib record
			options(dict) - options for request
		Returns:
			None
		"""

		url = 'https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}?apikey={}'.format(mms, self.alma_key)
		if options:
			option_string = ""
			for key in options.keys():
				url = url + "&"
				url = url + key + "=" + options[key]
		headers = {'content-type': 'application/xml'}
		r = requests.put( url, headers=headers, data = xml.encode("utf-8"))
		self.xml_data=  r.text
		self.status_code = r.status_code

	def get_holdings( self, mms, options ):

		"""
		Retrieves holdings for mms id
		Parameters:
			mms(str) - alma mms id
			options(dict) - options for request
		Returns:
			None
		"""
		url = 'https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/holdings?apikey={}'.format(mms, self.alma_key)
		if options:
			option_string = ""
			for key in options.keys():
				url = url + "&"
				url = url + key + "=" + options[key]
		r = requests.get( url)
		self.xml_data=  r.text
		self.status_code = r.status_code

	def get_holding(self, mms, holding, options):

		"""
		Retrieves holding by holding id
		Parameters:
			mms(str) - alma mms id
			holding(str) -alma holding id
			options(dict) - options for request
		Returns:
			None
		"""
		url = 'https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/holdings{}?apikey={}'.format(mms, holding, self.alma_key)
		if options:
			option_string = ""
			for key in options.keys():
				url = url + "&"
				url = url + key + "=" + options[key]
		r = requests.get( url)
		self.xml_data=  r.text
		self.status_code = r.status_code
	
	def get_items(self, mms,  holding, options):

		"""
		Retrieves items for mms id and holdings
		Parameters:
			mms(str) - alma mms id
			holding(str) Alma holding id
			options(dict) - options for request
		Returns:
			None
		"""
		url = 'https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/holdings/{}/items?apikey={}'.format(mms,holding, self.alma_key)
		if options:
			option_string = ""
			for key in options.keys():
				url = url + "&"
				url = url + key + "=" + options[key]
		r = requests.get( url)
		self.xml_data=  r.text
		self.status_code = r.status_code

	def get_item(self, mms, holding, item, options):

		"""
		Retrieves items for item id
		Parameters:
			mms(str) - alma mms id
			holding(str) Alma holding id
			item(str) - Alma item id
			options(dict) - options for request
		Returns:
			None
		"""
		url = 'https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/holdings/{}/items/{}?apikey={}'.format(mms,holding, item, self.alma_key)
		if options:
			option_string = ""
			for key in options.keys():
				url = url + "&"
				url = url + key + "=" + options[key]
		r = requests.get( url)
		self.xml_data=  r.text
		self.status_code = r.status_code
	
	def delete_holding(self, mms, holding):

		"""
		Deletes holding by holding id
		Parameters:
			mms(str) - alma mms id
			holding(str) Alma holding id
		Returns:
			None
		"""

		url = 'https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/holdings/{}?apikey={}'.format(mms, holding, self.alma_key)
		r = requests.delete( url )
		self.xml_data=  r.text
		self.status_code = r.status_code

	def delete_item( self, mms, holding, item):

		"""
		Deletes item by item id
		Parameters:
			mms(str) - Alma mms id
			holding(str) Alma holding id
			item(str) - Alma item id
		Returns:
			None
		"""

		url = 'https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/holdings/{}/items/{}?apikey={}'.format(mms, holding, item, self.alma_key)
		r = requests.delete( url )
		self.xml_data=  r.text
		self.status_code = r.status_code	


	def update_item(self, mms, holding, item, xml, options):

		"""Updates item with new item xml data

		Parameters:
			mms(str) - alma mms id
			xml(str) - xml for alma bib record
			options(dict) - options for request
		Returns:
			None
		"""

		url = 'https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/holdings/{}/items/{}?apikey={}'.format(mms, holding, item, self.alma_key)
		headers = {  'Content-Type':'application/xml'  }

		if options:
			option_string = ""
			for key in options.keys():
				url = url + "&"
				url = url + key + "=" + options[key]
		headers = {'content-type': 'application/xml'}
		r = requests.put( url, headers=headers, data = xml.encode("utf-8"))
		self.xml_data=  r.text
		self.status_code = r.status_code


	def get_reps(self, mms, options):

		"""
		Retrieves representations for mms 
		Parameters:
			mms(str) - alma mms id
			options(dict) - options for request
		Returns:
			None
		"""

		url = 'https://api-ap.hosted.exlibrisgroup.com/almaws/v1/bibs/{}/representations?apikey={}'.format(mms, self.alma_key)
		if options:
			option_string = ""
			for key in options.keys():
				url = url + "&"
				url = url + key + "=" + options[key]

		r = requests.get(url)
		self.xml_data=  r.text
		self.status_code = r.status_code

	

def main():

	"""Example of usage"""

	mms = "9918975967302836"

	my_api = Alma_tools(pr_key)

	#######################################
	my_api.get_bib(mms, {"limit":"100"})
	print(my_api.xml_data.encode("utf-8"))
	#######################################
	# my_api.update_bib(mms, my_api.xml_data, None)
	# print(my_api.status_code)
	#######################################
	my_api.get_reps(mms, None)
	print(my_api.xml_data.encode("utf-8"))


if __name__ == '__main__':
	main()