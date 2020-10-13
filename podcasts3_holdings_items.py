import os
import re
import io
import peewee
import requests
import hashlib
import codecs
import gspread
import time
import dateparser
from pymarc import parse_xml_to_array,record_to_xml, Field 
from datetime import datetime as dt
from podcast_models import Podcast, Episode, File
from bs4 import BeautifulSoup
from settings import file_folder, template_folder, working_folder, report_folder, config, logging, sb_key#
from openpyxl import load_workbook
from podcast_dict import podcasts_dict
from database_handler import DbHandler
from alma_tools import AlmaTools

class Holdings_items():

	def __init__(self, key, mms_list, update):

		self.mms = None
		self.item_pid  = None
		self.holding_id = None
		self.bib_data = None
		self.alma_key = None
		self.key = key
		self.hold_data = None
		self.enum =  None
		self.ie_num = None
		self.mms_list = mms_list
		self.holdings_list = []
		self.items_list = []
		self.year = None
		self.update = update
		self.mms_list = []

	
	def parsing_bib_xml(self):

		self.enum = None
		record = parse_xml_to_array(io.StringIO(self.bib_data))[0]
		self.podcast_name = record["490"]["a"].rstrip(", ")
		year = record["264"]["c"].strip("[]")
		logging(year)
		self.year = dateparser.parse(year)
		if record["830"]:
			my_alma = record["830"]["v"]
		elif record["800"]:
			my_alma = record["800"]["v"]
		self.date = dateparser.parse(my_alma)

		if not self.date:
			if len(re.findall(r"(?<!\d)\d{1}(?!\d)",my_alma)) == 1:
				self.enum = re.findall(r"(?<!\d)\d{1}(?!\d)",my_alma)[0]
			elif len(re.findall(r"(?<!\d)\d{2}(?!\d)",my_alma)) == 1:
				self.enum = re.findall(r"(?<!\d)\d{2}(?!\d)",my_alma)[0]
			elif len(re.findall(r"(?<!\d)\d{3}(?!\d)",my_alma)) == 1:
				self.enum =  re.findall(r"(?<!\d)\d{3}(?!\d)",my_alma)[0]
		
				


	def parse_holding(self):
		print("here888")

		"""Parsing holding data to find holding numbers. Makeing holding_list""" 

		self.holding_list = []
		hold_grab = BeautifulSoup( self.holding_data, 'lxml-xml' )
		try:
			print("finding holding numbers")
			self.hold_list = hold_grab.find_all("holding_id")
			for hold_line in self.hold_list:
				self.holding_list.append(hold_line.text)

		except AttributeError as e:
			statement =  "Error during creating bib {}, {}. Data: {} ".format ( type( e ),str( e ), str(self.holding_data) ) 
		


	def parsing_items_data(self):

		"""Searching for item numbers in items xml file. Makes item_list"""

		self.items_list = []
		item_grab = BeautifulSoup( self.item_data, 'lxml-xml' )
		try:
			items_list = item_grab.find("items").find_all("item")
			print("Finding item numbers")
			for item_line in items_list:
				self.items_list.append(item_line.attrs["link"].split("/")[-1])

		except Exceptions as e:
			print(str(e)) 

	
	def dups_deleting_routine(self):

		"""Running routine for deleting dupped items and holdings"""
		sb_mms = None
		if self.key=="sb":
			sb_mms = "9918602951502836"
		for mms in self.mms_list:
			self.mms = str(mms)
			my_alma=Alma_tools(self.key)
			my_alma.get_holding(self.mms)
			self.holding_data = my_alma.xml_data
			self.parse_holding()
			print(self.holding_list)
			if len(self.holding_list) >1:
				print("The number of holdings is ",len(self.holding_list))
				for ind in range(len(self.holding_list)-1):
					print(self.holding_list[ind])
					self.holding_id = self.holding_list[ind]
					my_alma.get_items(self.mms,self.holding)
					self.item_data = my_alma.xml_data
					self.parsing_items_data()
					for item in self.items_list:
						self.item_pid  = item
						my_alma.get_item(self.mms, self.holding, self.item)
						self.item_data=my_alma.item_data
						self.parsing_item_data()
						my_alma.update_item(self.mms, self.holding, self.item,self.item_data)
						my_alma.delete_item(self.mms, self.holding, self.item)
						print("item " + self.item_pid  + " deleted")
						with open('deleted.txt',"a") as fl:
							fl.write(self.item)
							fl.write("\n")
					self.delete_holdings()
					print("holding " + self.holding_id + " deleted")
					with open('deleted.txt',"a") as fl:
						fl.write(self.item)
						fl.write("\n")

			elif len(self.holding_list)==1:
				print("The number of holdins is 1")
				
				self.holding_id = self.holding_list[0]
				print(self.holding)
				self.get_items()
				self.parsing_items_data()
				if len(self.items_list)>1:
					print("The number of items is ", len(self.items_list))
					for ind in range(len(self.items_list)-1):
						self.item_pid  = self.items_list[ind]
						self.get_item()
						self.parsing_item_data()
						self.update_item()
						self.delete_item()
						print("Item ", self.item, " deleted")
						with open('deleted.txt',"a") as fl:
							fl.write(self.item)
							fl.write("\n")
				else:
					print("Number of items is ", len(self.items_list))
			else:
				print("No holdings")
					

	

	def item_routine(self):



		sb_mms = None
		if self.key=="sb": 
			sb_mms = "9918602951502836"
		for pod_list  in  self.mms_list:
			if pod_list and pod_list != [None, None, None]:
				self.holding_list = []
				print(pod_list)
				self.holding_id = pod_list[1]
				self.item_pid  = pod_list[2]
				self.mms = pod_list[0]
				print(self.mms)
				my_alma = Alma_tools(self.key)
				my_alma.get_bib( self.mms)
				self.bib_data= my_alma.xml_data
				print(self.bib_data.encode("utf-8"))
				self.parsing_bib_xml()
				print(self.date)
				print(self.enum)
				my_alma.get_reps(self.mms)
				print(my_alma.xml_data)
				print("here0")
				ie_grab = BeautifulSoup(my_alma.xml_data, "lxml")
				print("here1")
				try:
					print("here3")
					self.ie_num = ie_grab.find_all( 'originating_record_id' )[0]
					if len(ie_grab.find_all( 'originating_record_id' ))>1:
						print("Possible duplicated digital representation")
					q = Episode.update(ie_num = self.ie_num).where(Episode.mis_mms == self.mms)
					q.execute()
					print("here4")

				except:
					pass
				if not self.ie_num:
					print("here5")
					print("There is no representation yet")
				else:
					if self.mms:
						print("here6")
						if sb_mms:
							self.mms = str(sb_mms)
						with open(os.path.join(template_folder, "holding.xml")) as hold_data:
							self.hold_data = hold_data.read()
						my_alma.get_holdings(self.mms,{"limit":"100"})
						self.holding_data = my_alma.xml_data
						self.parse_holding()
						print("here7")
						my_alma.get_bib(self.mms)
						self.bib_data = my_alma.xml_data
						self.parsing_bib_xml()
						for spec_char in ["/",":","-" ]:
							if spec_char in self.podcast_name and not self.podcast_name.startswith("Human") and not self.podcast_name.startswith("Back to the"):
								self.podcast_name = self.podcast_name.split(spec_char)[0].rstrip(" ") 
						self.serial_pol = podcasts_dict[self.podcast_name]["serial_pol"]
						print(self.serial_pol)
						print("here8")
						print(self.holdings_list)
						print("here9")
						if self.holdings_list != []:
							self.holding_id = self.holdings_list[0]
						if not self.holding_id and self.mms:
							print("here10")
							print(self.mms)
							if not self.update:
								my_alma.create_holding(self.mms)
								holding_grab = BeautifulSoup( my_alma.xml_data, 'lxml-xml' )
								self.holding= holding_grab.find( 'holding' ).find( 'holding_id' ).string
								db_handler = DbHAndler()
								db_hangler.db_update_holding(self.mms, self.holding)

						print("here11")
						my_alma.get_items(self.mms, self.holding)
						print("here12")
						self.item_pid  = my_alma.xml_data
						print(self.item)
						print("here133")
						print(self.items_list)
						if self.items_list != [] and self.items_list:
							self.item_pid  = self.items_list[0]

						if not self.item_pid  and self.holding_id and self.mms:
								print("herr13")
								polstring = "<po_line>{}</po_line>".format(self.serial_pol)
								if  self.enum:
									chron_j = ""
									chron_k = ""
									chron_i = dt.strftime(self.year, "%Y")
									description = "<description>no. {} ({})</description>)".format(self.enum, chron_i)
									enum = self.enum
								else:
									
									enum = ""
									if self.date:
										chron_j = dt.strftime(self.date,"%m")
										chron_k = dt.strftime(self.date,"%d")
										chron_i = dt.strftime(self.date,"%Y")
									else:
										chron_j = ""
										chron_k = ""
										chron_i = dt.strftime(self.year,"%Y")
									description = "<description>{} {} {}</description>)".format( chron_i, chron_j,chron_k)
									chron_i_stat = "<chronology_i>{}</chronology_i>".format( chron_i )
									chron_j_stat = "<chronology_j>{}</chronology_j>".format( chron_j )
									chron_k_stat = "<chronology_k>{}</chronology_k>".format( chron_k )
									enum_stat = "<enumeration_b>{}</enumeration_b>".format( enum )
									time_substitute_statement = "<creation_date>{}</creation_date>".format(str(dt.now().strftime( '%Y-%m-%d')))
									receiving_stat = "<arrival_date>{}</arrival_date>".format(str(dt.now().strftime( '%Y-%m-%d')))
									with open(os.path.join(working_folder,"assets", "templates","item.xml"), "r") as data:
										item_data = data.read()
										item_data = item_data.replace("<creation_date></creation_date>", time_substitute_statement)
										item_data = item_data.replace("<po_line></po_line>", polstring )
										item_data = item_data.replace("<enumeration_b></enumeration_b>", enum_stat )
										item_data = item_data.replace("<chronology_i></chronology_i>", chron_i_stat )
										item_data = item_data.replace("<chronology_j></chronology_j>", chron_j_stat )
										item_data = item_data.replace("<chronology_k></chronology_k>", chron_k_stat )
										item_data = item_data.replace("<description></description>", description )
										item_data = item_data.replace("<arrival_date></arrival_date>", receiving_stat )
										self.item_data = item_data
										#print(self.item_data.encode("utf-8"))
										if not update:
											my_alma.create_item(self.mms, self.holding)
											item_grab = BeautifulSoup(my_alma.xml_data)
											self.item_pid  = item_grab.find('item').find( 'item_data' ).find( 'pid' ).string 
											db_hangler.db_update_item_id(self.mms, self.item)
											self.mms_list.append(self.mms)
										else:
											print(self.item_data)
											quit()
											my_alma.update_item(self.mms, self.holding, self.item, self.item_date)
						print("herr14")

						report_name = "report"+str(dt.now().strftime("_%d%m%Y_%H_%M"))+".txt"

						with open(os.path.join(report_folder, report_name),"a") as f:
							f.write("{}|{}|{}|{}".format(self.mms, self. holding, self.item, self.ie_num))
							f.write("\n")		

def main():

	my_podcasts = DbHandler().db_reader(["mis_mms", "holdings", "item"], None, True)
	# for el in my_alma:
	# 	print(el)
	mms_list = [[el["mis_mms"],el["holdings"],el["item"]] for el in my_podcasts]
	update = True
	my_item = Holdings_items("prod", mms_list, update)
	my_item.item_routine()
			



if __name__ == '__main__':

	
	main()